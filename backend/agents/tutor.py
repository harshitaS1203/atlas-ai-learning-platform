class Tutor:

    def __init__(self, client, memory):

        self.client = client
        self.memory = memory

    def teach(
        self,
        topic,
        level="beginner"
    ):

        print(
            "Tutor started",
            flush=True
        )

        learning_context = self.memory.get_learning_context(
            topic
        )

        if learning_context:

            print(
                "Previous learning history found.",
                flush=True
            )

        else:

            print(
                "No previous learning history found.",
                flush=True
            )

        prompt = f"""
You are Atlas, an AI learning tutor.

Teach this topic to a {level} learner:

{topic}

Previous learning information:

{learning_context}

Teaching rules:

1. Start with intuition.
2. Explain the technical concept.
3. Give a simple example.
4. Avoid unnecessary jargon.
5. If previous learning information exists, focus extra attention
   on the concepts the student previously struggled with.
6. Do not repeat material unnecessarily if the student already
   understands it.
7. End with two questions to test understanding.

If there is no previous learning information, teach the topic
normally from the basics.
"""

        print(
            "Sending tutor request...",
            flush=True
        )

        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        print(
            "Tutor response received!",
            flush=True
        )

        return response.text