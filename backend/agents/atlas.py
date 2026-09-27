from backend.agents.supervisor import Supervisor
from backend.agents.tutor import Tutor
from backend.agents.evaluator import Evaluator
from backend.agents.researcher import Researcher
from backend.agents.memory import Memory


class Atlas:

    def __init__(self, client):

        self.client = client

        self.memory = Memory()

        self.supervisor = Supervisor()

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

        print(
            "Atlas initialized successfully!",
            flush=True
        )