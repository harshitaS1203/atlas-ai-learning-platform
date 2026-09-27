import json


class Evaluator:

    def __init__(self, client):
        self.client = client

    def generate_quiz(self, topic):

        print("Evaluator started", flush=True)

        if "typed" in str(topic).lower() or "written" in str(topic).lower():
            prompt = f"""You are Atlas, an AI learning evaluator.

The student wants to test their understanding with a Typed Answer quiz:

{topic}

Create exactly 2 Typed Answer conceptual questions.

Return ONLY valid JSON array with 2 objects in this structure:
[
  {{"question": "Question 1 text"}},
  {{"question": "Question 2 text"}}
]
"""
        else:
            prompt = f"""You are Atlas, an AI learning evaluator.

The student wants to test their understanding with a Multiple Choice (MCQ) quiz:

{topic}

Create Productive 5 Multiple Choice Questions.

Return ONLY valid JSON array with 5 objects in this structure:
[
  {{
    "question": "Question 1 text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }},
  {{
    "question": "Question 2 text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }},
  {{
    "question": "Question 3 text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }},
  {{
    "question": "Question 4 text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }},
  {{
    "question": "Question 5 text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }}
]
"""

        print("Sending quiz request...", flush=True)

        from google.genai import types
        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8)
        )

        print("Quiz response received!", flush=True)

        return response.text

    def evaluate_answers(self, topic, questions, answers):

        print("Evaluator started answer evaluation", flush=True)

        prompt = f"""
You are Atlas, an AI learning evaluator.

Topic:
{topic}

Quiz questions:
{questions}

Student submitted answers:
{answers}

Carefully evaluate the student's actual submitted answers for each question.

Rules:
1. "score" MUST be an integer between 0 and 10 representing overall score:
   - For a 2-question Typed Answer quiz: award 5 points per correctly answered question (0, 5, or 10).
   - For a 5-question MCQ quiz: award 2 points per correctly answered question (0, 2, 4, 6, 8, or 10).
   - If the student answered "idk", "idk pls help", blank, or incorrect answers, give 0 points for those questions.
2. "strengths": List ONLY concepts from questions that the student ACTUALLY answered correctly.
   - CRITICAL: If the student wrote "idk", "idk pls help", blank, or gave completely wrong answers, DO NOT list any strengths! Return ["No concepts mastered in this attempt"].
3. "weaknesses": List concepts corresponding to the questions the student got wrong, left blank, or answered with "idk".
4. "recommendation": ONE specific topic or concept from the document the student should review next.
5. "detailed_evaluation": A concise 2-sentence summary explaining why the student received this score based on their specific answers.

Return ONLY valid JSON in exactly this structure:
{{
    "score": 0,
    "strengths": [],
    "weaknesses": [],
    "recommendation": "",
    "detailed_evaluation": ""
}}
"""

        print("Sending evaluation request...", flush=True)

        response = self.client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        print("Evaluation response received!", flush=True)

        result_text = response.text.strip()

        try:
            result = json.loads(result_text)

        except json.JSONDecodeError:

            start = result_text.find("{")
            end = result_text.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError(
                    "Evaluator did not return valid JSON."
                )

            result = json.loads(
                result_text[start:end]
            )

        return result