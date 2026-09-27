import json
import re
from pathlib import Path


class Memory:

    def __init__(
        self,
        memory_file="backend/memory/user_memory.json"
    ):

        BASE_DIR = Path(__file__).resolve().parent.parent.parent

        self.memory_path = BASE_DIR / memory_file

        self.memory_path.parent.mkdir(
            exist_ok=True
        )

        if not self.memory_path.exists():

            self.memory = {
                "learning_history": []
            }

            self._save()

        else:

            with open(
                self.memory_path,
                "r"
            ) as file:

                self.memory = json.load(file)

            if "learning_history" not in self.memory:

                self.memory["learning_history"] = []

                if "topics" in self.memory:

                    for topic, result in self.memory["topics"].items():

                        converted_result = {
                            "topic": topic,
                            "score": result.get("score", 0),
                            "strengths": result.get(
                                "strengths",
                                []
                            ),
                            "weaknesses": result.get(
                                "weaknesses",
                                []
                            ),
                            "recommendation": result.get(
                                "recommendation",
                                ""
                            )
                        }

                        self.memory[
                            "learning_history"
                        ].append(
                            converted_result
                        )

                self._save()

    # ---------------------------------
    # Save memory
    # ---------------------------------

    def _save(self):

        with open(
            self.memory_path,
            "w"
        ) as file:

            json.dump(
                self.memory,
                file,
                indent=4
            )

    # ---------------------------------
    # Save learning result
    # ---------------------------------

    def save_learning_result(
        self,
        topic,
        score,
        strengths,
        weaknesses,
        recommendation
    ):

        learning_result = {
            "topic": topic,
            "score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": recommendation
        }

        if "learning_history" not in self.memory:

            self.memory["learning_history"] = []

        self.memory[
            "learning_history"
        ].append(
            learning_result
        )

        self._save()

    # ---------------------------------
    # Normalize topic text
    # ---------------------------------

    def _normalize_topic(self, text):

        if not text:
            return set()

        text = text.lower()

        # Remove common instructional phrases.
        phrases = [
            "quiz me on",
            "test me on",
            "test my knowledge on",
            "teach me",
            "explain",
            "help me understand",
            "help me learn",
            "learn about",
            "research",
            "research the concept of",
            "research about",
            "tell me about",
            "what is",
            "what are",
            "how does",
            "how do",
            "please",
            "again",
            "one more time",
            "in simple words",
            "as a beginner",
            "to me"
        ]

        for phrase in phrases:

            text = text.replace(
                phrase,
                " "
            )

        # Remove punctuation.
        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        # Split into words.
        words = text.split()

        # Words that describe the request rather than the topic.
        stop_words = {
            "the",
            "a",
            "an",
            "on",
            "about",
            "of",
            "and",
            "or",
            "with",
            "for",
            "to",
            "my",
            "me",
            "i",
            "you",
            "your",
            "this",
            "that",
            "it",
            "is",
            "are",
            "was",
            "were",
            "be",
            "from",
            "in",
            "at",
            "by",
            "into",
            "focus",
            "focused",
            "areas",
            "area",
            "struggled",
            "struggle",
            "struggledwith",
            "previous",
            "weaknesses",
            "weakness",
            "strengths",
            "strength",
            "please",
            "give",
            "want",
            "know",
            "understanding",
            "understand"
        }

        meaningful_words = []

        for word in words:

            if word not in stop_words:

                meaningful_words.append(
                    word
                )

        return set(
            meaningful_words
        )

    # ---------------------------------
    # Find topic history
    # ---------------------------------

    def get_topic_history(self, topic):

        history = self.memory.get(
            "learning_history",
            []
        )

        if not history:

            return []

        current_words = self._normalize_topic(
            topic
        )

        if not current_words:

            return []

        matching_results = []

        for result in history:

            stored_topic = result.get(
                "topic",
                ""
            )

            stored_words = self._normalize_topic(
                stored_topic
            )

            if not stored_words:

                continue

            # Exact normalized match.
            if current_words == stored_words:

                matching_results.append(
                    result
                )

                continue

            # If all words from the stored topic
            # appear in the current request, consider
            # it the same learning topic.
            if stored_words.issubset(
                current_words
            ):

                matching_results.append(
                    result
                )

                continue

            # Also support the reverse situation:
            # if the current topic is contained in
            # the stored topic.
            if current_words.issubset(
                stored_words
            ):

                matching_results.append(
                    result
                )

        return matching_results

    # ---------------------------------
    # Build context for Tutor
    # ---------------------------------

    def get_learning_context(self, topic):

        history = self.get_topic_history(
            topic
        )

        if not history:

            return ""

        latest = history[-1]

        context = f"""
Previous learning history for this topic:

Previous Score:
{latest.get("score", "Unknown")}/10

Concepts the student understands:
{latest.get("strengths", [])}

Concepts the student struggled with:
{latest.get("weaknesses", [])}

Recommended next topic:
{latest.get("recommendation", "")}
"""

        return context

    # ---------------------------------
    # Get complete memory
    # ---------------------------------

    def get_all_memory(self):

        return self.memory