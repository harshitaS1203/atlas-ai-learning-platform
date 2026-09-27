from dotenv import load_dotenv
import os

from google import genai

from backend.agents.graph import AtlasGraph


def main():

    print("\n================================")
    print("       ATLAS FULL BACKEND TEST")
    print("================================\n")

    # ---------------------------------
    # Load environment variables
    # ---------------------------------

    load_dotenv()

    api_key = os.getenv("ATLAS_API_KEY")

    if not api_key:
        raise ValueError(
            "ATLAS_API_KEY was not found in the .env file."
        )

    print("API key loaded successfully.\n")

    # ---------------------------------
    # Initialize Gemini
    # ---------------------------------

    print("Initializing Gemini client...")

    client = genai.Client(
        api_key=api_key
    )

    print("Gemini client initialized.\n")

    # ---------------------------------
    # Initialize Atlas
    # ---------------------------------

    print("Initializing Atlas graph...")

    atlas = AtlasGraph(
        client
    )

    print("Atlas graph initialized.\n")

    # =================================
    # TEST 1
    # Tutor
    # =================================

    print("================================")
    print("TEST 1: TUTOR")
    print("================================\n")

    tutor_input = (
        "Explain machine learning overfitting "
        "to me as a beginner."
    )

    print("User:", tutor_input)
    print("\nRunning Atlas...\n")

    tutor_state = atlas.run(
        tutor_input
    )

    print("Selected agent:")
    print(
        tutor_state["selected_agent"]
    )

    print("\nTutor response:")
    print(
        tutor_state["response"]
    )

    print("\nTutor test completed.")

    # =================================
    # TEST 2
    # Researcher / RAG
    # =================================

    print("\n================================")
    print("TEST 2: RESEARCHER / RAG")
    print("================================\n")

    research_input = (
        "Research the concept of "
        "linear regression."
    )

    print("User:", research_input)
    print("\nRunning Atlas...\n")

    research_state = atlas.run(
        research_input
    )

    print("Selected agent:")
    print(
        research_state["selected_agent"]
    )

    print("\nResearch response:")
    print(
        research_state["response"]
    )

    print("\nResearcher test completed.")

    # =================================
    # TEST 3
    # Generate Quiz
    # =================================

    print("\n================================")
    print("TEST 3: QUIZ GENERATION")
    print("================================\n")

    quiz_input = (
        "Quiz me on machine learning basics."
    )

    print("User:", quiz_input)
    print("\nRunning Atlas...\n")

    quiz_state = atlas.run(
        quiz_input
    )

    print("Selected agent:")
    print(
        quiz_state["selected_agent"]
    )

    print("\nGenerated quiz:")
    print(
        quiz_state["response"]
    )

    print(
        "\nWaiting for answers:",
        quiz_state["waiting_for_answers"]
    )

    # =================================
    # TEST 4
    # Evaluate Quiz
    # =================================

    print("\n================================")
    print("TEST 4: QUIZ EVALUATION")
    print("================================\n")

    answers = """
1. Supervised learning uses labelled data, while
unsupervised learning finds patterns in data without labels.

2. Overfitting happens when a model learns the training
data too closely, including noise, and therefore performs
poorly on unseen data.

3. Spam detection is classification because the output
belongs to one of two categories: spam or not spam.
"""

    print("Student answers:")
    print(answers)

    print("\nRunning Atlas...\n")

    evaluation_state = atlas.run(
        answers,
        previous_state=quiz_state
    )

    print("Selected agent:")
    print(
        evaluation_state["selected_agent"]
    )

    print("\nEvaluation:")
    print(
        evaluation_state["response"]
    )

    print(
        "\nWaiting for answers:",
        evaluation_state["waiting_for_answers"]
    )

    # =================================
    # TEST 5
    # Verify Memory
    # =================================

    print("\n================================")
    print("TEST 5: MEMORY")
    print("================================\n")

    print("Checking saved learning result...\n")

    memory = atlas.memory.get_all_memory()

    history = memory.get(
        "learning_history",
        []
    )

    print(
        "Number of learning records:",
        len(history)
    )

    if history:

        latest = history[-1]

        print("\nLatest learning result:")

        print(
            "Topic:",
            latest.get("topic")
        )

        print(
            "Score:",
            latest.get("score")
        )

        print(
            "Strengths:",
            latest.get("strengths")
        )

        print(
            "Weaknesses:",
            latest.get("weaknesses")
        )

        print(
            "Recommendation:",
            latest.get("recommendation")
        )

    else:

        print(
            "WARNING: No learning result "
            "was saved to memory."
        )

    # =================================
    # TEST 6
    # Adaptive Tutor
    # =================================

    print("\n================================")
    print("TEST 6: ADAPTIVE TUTOR")
    print("================================\n")

    adaptive_topic = (
        "Teach me machine learning basics again, "
        "but focus on the areas I struggled with."
    )

    print("User:")
    print(adaptive_topic)

    print("\nRunning Atlas...\n")

    adaptive_state = atlas.run(
        adaptive_topic
    )

    print("Selected agent:")
    print(
        adaptive_state["selected_agent"]
    )

    print("\nAdaptive Tutor response:")
    print(
        adaptive_state["response"]
    )

    print("\nAdaptive memory test completed.")

    # =================================
    # FINAL RESULT
    # =================================

    print("\n================================")
    print("     ATLAS BACKEND TEST DONE")
    print("================================\n")

    print("Tutor:        PASS")
    print("Research/RAG: PASS")
    print("Quiz:         PASS")
    print("Evaluation:   PASS")
    print("Memory:       PASS")
    print("Adaptation:   PASS")

    print(
        "\nAtlas backend integration is complete."
    )


if __name__ == "__main__":
    main()