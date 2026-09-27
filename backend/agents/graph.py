from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from backend.agents.supervisor import Supervisor
from backend.agents.tutor import Tutor
from backend.agents.evaluator import Evaluator
from backend.agents.researcher import Researcher
from backend.agents.memory import Memory


class AtlasState(TypedDict):

    user_input: str
    selected_agent: str
    response: str
    topic: str
    quiz: str
    waiting_for_answers: bool
    evaluation: Optional[dict]
    document_paths: list[str]


class AtlasGraph:

    def __init__(self, client):

        print(
            "Initializing Atlas LangGraph...",
            flush=True
        )

        self.client = client

        self.supervisor = Supervisor()

        self.memory = Memory()

        self.tutor = Tutor(
            client,
            self.memory
        )

        self.evaluator = Evaluator(
            client
        )

        self.researcher = Researcher(
            client,
            "backend/knowledge_base/ML_Textbook.pdf"
        )

        self.graph = self._build_graph()

        print(
            "Atlas LangGraph initialized successfully!",
            flush=True
        )

    # ============================================================
    # SUPERVISOR NODE
    # ============================================================

    def supervisor_node(
        self,
        state: AtlasState
    ):

        print(
            "\n===== SUPERVISOR NODE =====",
            flush=True
        )

        # Quiz answer flow
        if state["waiting_for_answers"]:

            print(
                "Quiz answers detected.",
                flush=True
            )

            return {
                "selected_agent": "evaluator"
            }

        # --------------------------------------------------------
        # CHECK FOR UPLOADED DOCUMENTS
        # --------------------------------------------------------

        document_paths = state.get(
            "document_paths",
            []
        )

        has_documents = len(
            document_paths
        ) > 0

        print(
            "Uploaded documents:",
            document_paths,
            flush=True
        )

        print(
            "Has documents:",
            has_documents,
            flush=True
        )

        # --------------------------------------------------------
        # SUPERVISOR DECISION
        # --------------------------------------------------------

        selected_agent = self.supervisor.decide(
            state["user_input"],
            self.memory,
            has_documents=has_documents
        )

        print(
            "Selected agent:",
            selected_agent,
            flush=True
        )

        return {
            "selected_agent": selected_agent
        }

    # ============================================================
    # TUTOR NODE
    # ============================================================

    def tutor_node(
        self,
        state: AtlasState
    ):

        print(
            "\n===== TUTOR NODE =====",
            flush=True
        )

        response = self.tutor.teach(
            state["user_input"]
        )

        return {
            "response": response
        }

    # ============================================================
    # RESEARCHER NODE
    # ============================================================

    def researcher_node(
        self,
        state: AtlasState
    ):

        print(
            "\n===== RESEARCHER NODE =====",
            flush=True
        )

        document_paths = state.get(
            "document_paths",
            []
        )

        # --------------------------------------------------------
        # USER PDF
        # --------------------------------------------------------

        if document_paths:

            print(
                "Using uploaded PDF documents:",
                flush=True
            )

            for path in document_paths:

                print(
                    f"  - {path}",
                    flush=True
                )

            self.researcher.set_user_documents(
                document_paths
            )

        # --------------------------------------------------------
        # BUILT-IN KNOWLEDGE BASE
        # --------------------------------------------------------

        else:

            print(
                "Using built-in knowledge base.",
                flush=True
            )

        # --------------------------------------------------------
        # RAG RESEARCH
        # --------------------------------------------------------

        result = self.researcher.research(
            state["user_input"]
        )

        print(
            "Researcher completed.",
            flush=True
        )

        return {
            "response": result["answer"]
        }

    # ============================================================
    # EVALUATOR NODE
    # ============================================================

    def evaluator_node(
        self,
        state: AtlasState
    ):

        print(
            "\n===== EVALUATOR NODE =====",
            flush=True
        )

        # --------------------------------------------------------
        # GENERATE QUIZ
        # --------------------------------------------------------

        if not state["waiting_for_answers"]:

            print(
                "Generating quiz...",
                flush=True
            )

            quiz = self.evaluator.generate_quiz(
                state["user_input"]
            )

            return {
                "response": quiz,
                "quiz": quiz,
                "topic": state["user_input"],
                "waiting_for_answers": True
            }

        # --------------------------------------------------------
        # EVALUATE ANSWERS
        # --------------------------------------------------------

        print(
            "Evaluating quiz answers...",
            flush=True
        )

        evaluation = self.evaluator.evaluate_answers(
            state["topic"],
            state["quiz"],
            state["user_input"]
        )

        evaluation_text = (
            f"Overall Score: "
            f"{evaluation['score']}/10\n\n"
            f"Strengths:\n"
        )

        for strength in evaluation["strengths"]:

            evaluation_text += (
                f"- {strength}\n"
            )

        evaluation_text += (
            "\nWeaknesses:\n"
        )

        for weakness in evaluation["weaknesses"]:

            evaluation_text += (
                f"- {weakness}\n"
            )

        evaluation_text += (
            "\nRecommendation:\n"
            f"- {evaluation['recommendation']}\n\n"
            "Detailed Evaluation:\n"
            f"{evaluation['detailed_evaluation']}"
        )

        return {
            "response": evaluation_text,
            "evaluation": evaluation,
            "waiting_for_answers": False
        }

    # ============================================================
    # MEMORY NODE
    # ============================================================

    def memory_node(
        self,
        state: AtlasState
    ):

        print(
            "\n===== MEMORY NODE =====",
            flush=True
        )

        evaluation = state["evaluation"]

        if evaluation:

            print(
                "Saving evaluation to memory...",
                flush=True
            )

            self.memory.save_learning_result(
                topic=state["topic"],
                score=evaluation["score"],
                strengths=evaluation["strengths"],
                weaknesses=evaluation["weaknesses"],
                recommendation=evaluation["recommendation"]
            )

            print(
                "Learning result saved to memory!",
                flush=True
            )

        else:

            print(
                "Retrieving memory...",
                flush=True
            )

        return {
            "response": state["response"]
        }

    # ============================================================
    # ROUTING
    # ============================================================

    def route_from_supervisor(
        self,
        state: AtlasState
    ):

        selected_agent = state[
            "selected_agent"
        ]

        if selected_agent == "tutor":
            return "tutor"

        if selected_agent == "researcher":
            return "researcher"

        if selected_agent == "evaluator":
            return "evaluator"

        if selected_agent == "memory":
            return "memory"

        return "tutor"

    # ============================================================
    # EVALUATOR ROUTING
    # ============================================================

    def route_after_evaluator(
        self,
        state: AtlasState
    ):

        if state["waiting_for_answers"]:

            return "end"

        if state["evaluation"]:

            return "memory"

        return "end"

    # ============================================================
    # BUILD GRAPH
    # ============================================================

    def _build_graph(self):

        workflow = StateGraph(
            AtlasState
        )

        workflow.add_node(
            "supervisor",
            self.supervisor_node
        )

        workflow.add_node(
            "tutor",
            self.tutor_node
        )

        workflow.add_node(
            "researcher",
            self.researcher_node
        )

        workflow.add_node(
            "evaluator",
            self.evaluator_node
        )

        workflow.add_node(
            "memory",
            self.memory_node
        )

        workflow.set_entry_point(
            "supervisor"
        )

        workflow.add_conditional_edges(
            "supervisor",
            self.route_from_supervisor,
            {
                "tutor": "tutor",
                "researcher": "researcher",
                "evaluator": "evaluator",
                "memory": "memory"
            }
        )

        workflow.add_edge(
            "tutor",
            END
        )

        workflow.add_edge(
            "researcher",
            END
        )

        workflow.add_conditional_edges(
            "evaluator",
            self.route_after_evaluator,
            {
                "memory": "memory",
                "end": END
            }
        )

        workflow.add_edge(
            "memory",
            END
        )

        return workflow.compile()

    # ============================================================
    # RUN
    # ============================================================

    def run(
        self,
        user_input,
        previous_state=None
    ):

        if previous_state is None:

            state = {
                "user_input": user_input,
                "selected_agent": "",
                "response": "",
                "topic": "",
                "quiz": "",
                "waiting_for_answers": False,
                "evaluation": None,
                "document_paths": []
            }

        else:

            state = previous_state.copy()

            state["user_input"] = user_input

            state["response"] = ""

            state["evaluation"] = None

            state["document_paths"] = state.get(
                "document_paths",
                []
            )

        final_state = self.graph.invoke(
            state
        )

        return final_state
