import requests
from bs4 import BeautifulSoup


class BaseAgent:
    def __init__(self, topic_name):
        self.topic_name = topic_name
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def fetch_titles(self, url):
        if not url:
            return f"[{self.topic_name}] Error: No URL found in config.\n\n"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scrapes the first 3 titles from ArXiv
            titles = [t.text.strip() for t in soup.find_all('div', class_='list-title')[:3]]

            result = f"[{self.topic_name} Updates]\n"
            if not titles:
                return result + "No new articles found today.\n\n"

            for i, title in enumerate(titles, 1):
                clean_title = title.replace('Title:', '').strip()
                result += f"{i}. {clean_title}\n"
            return result + "\n"
        except Exception as e:
            return f"Error fetching {self.topic_name}: {e}\n\n"