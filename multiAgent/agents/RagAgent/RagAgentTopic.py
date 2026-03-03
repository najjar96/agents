from agents.base_agent import BaseAgent

class RagAgent(BaseAgent):
    def __init__(self):
        super().__init__("RAG & NLP")

    def get_updates(self, url):
        return self.fetch_titles(url)