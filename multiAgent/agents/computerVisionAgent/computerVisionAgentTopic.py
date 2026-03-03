from agents.base_agent import BaseAgent

class CVAgent(BaseAgent):
    def __init__(self):
        super().__init__("Computer Vision")

    def get_updates(self, url):
        return self.fetch_titles(url)