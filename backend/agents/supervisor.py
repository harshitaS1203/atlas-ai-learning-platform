class Supervisor:

    def __init__(self):

        self.available_agents = [
            "researcher",
            "tutor",
            "evaluator",
            "memory"
        ]

    def decide(
        self,
        user_input,
        memory=None,
        has_documents=False
    ):

        text = user_input.lower()

        # ============================================================
        # PDF / DOCUMENT PRIORITY
        # ============================================================

        # If the user has uploaded a PDF, questions about the
        # uploaded material should go to the Researcher.
        document_keywords = [
            "pdf",
            "document",
            "file",
            "uploaded",
            "this",
            "summarize",
            "summary",
            "according to",
            "from the document",
            "from the pdf",
            "in the pdf",
            "based on the pdf",
            "based on this",
            "what does it say",
            "explain this"
        ]

        if has_documents and any(
            keyword in text
            for keyword in document_keywords
        ):
            return "researcher"

        # If a document exists, default document-related questions
        # to the Researcher rather than generic tutoring.
        if has_documents:
            return "researcher"

        # ============================================================
        # MEMORY
        # ============================================================

        memory_keywords = [
            "what do i know",
            "my progress",
            "my score",
            "what did i struggle with",
            "my weaknesses",
            "my strengths",
            "remember",
            "my history"
        ]

        if any(
            keyword in text
            for keyword in memory_keywords
        ):
            return "memory"

        # ============================================================
        # EVALUATOR
        # ============================================================

        evaluator_keywords = [
            "quiz",
            "test me",
            "test my knowledge",
            "evaluate me",
            "questions"
        ]

        if any(
            keyword in text
            for keyword in evaluator_keywords
        ):
            return "evaluator"

        # ============================================================
        # RESEARCH
        # ============================================================

        research_keywords = [
            "research",
            "find information",
            "search",
            "look up",
            "sources",
            "information about"
        ]

        if any(
            keyword in text
            for keyword in research_keywords
        ):
            return "researcher"

        # ============================================================
        # TUTOR
        # ============================================================

        tutor_keywords = [
            "teach",
            "explain",
            "what is",
            "how does",
            "help me understand",
            "learn"
        ]

        if any(
            keyword in text
            for keyword in tutor_keywords
        ):
            return "tutor"

        return "tutor"
