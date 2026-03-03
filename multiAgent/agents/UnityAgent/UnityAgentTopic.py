from agents.base_agent import BaseAgent

class UnityAgent(BaseAgent):
    def __init__(self):
        super().__init__("3D & Unity Vision")

    def get_updates(self, url):
        return self.fetch_titles(url)