import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- ROLES AND CONSTRAINTS ---
YEAR_CONSTRAINT = ["2026", "2027"]

ROLES = {
    'CV': "System Architect (Focus: MCP, Memory, RAG Architecture)",
    'UNITY': "Spatial Computing Engineer (Focus: 3D, Guided Data, Depth, Unity)",
    'AGENT': "Agentic AI Specialist (Focus: Autonomous Multi-Agent Systems, Xcode)",
    'RAG': "Vision/VLM/GenAI Researcher (Focus: Generative models & Multimodal)"
}

# KEYWORDS: Ordered from Most Specific to Most General
KEYWORDS = {
    'CV': ['mcp', 'memory', 'retrieval-augmented', 'knowledge graph', 'context window'],
    'UNITY': ['spatial', '3d', 'guided data', 'gaussian', 'nerf', 'depth', 'point cloud', 'unity', '3d'],
    'AGENT': ['multi-agent', 'swarm', 'autonomous', 'xcode', 'ios', 'agent workflow', 'ai engineer'],
    'RAG': ['vision', 'vlm', 'gen ai', 'diffusion', 'multimodal', 'llm']
}


def scrape_any_site(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = []
        for h in soup.find_all(['h1', 'h2', 'h3', 'div'], class_=['list-title', 'title', 'headline']):
            text = h.get_text(strip=True)
            if len(text) > 20:
                # Ensure it's not an old paper (2023-2025)
                if not any(y in text for y in ["2023", "2024", "2025"]):
                    titles.append(text)
        return list(set(titles[:10]))
    except:
        return []


def send_email(recipient, subject, content, role_desc):
    if not content.strip() or not recipient: return
    sender = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')

    header = f"ROLE: {role_desc}\nDATE TARGET: 2026+\n"
    header += "=" * 50 + "\n\n"

    msg = MIMEMultipart()
    msg['Subject'] = f"[2026 Intelligence] {subject}"
    msg.attach(MIMEText(header + content, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient.split(','), msg.as_string())
            print(f"Dispatched {subject} to {recipient}")
    except Exception as e:
        print(f"Mail Error: {e}")


def job():
    urls = []
    for i in range(1, 6):
        chunk = os.getenv(f'RES_{i}', '')
        if chunk: urls.extend([u.strip() for u in chunk.split(',') if u.strip()])

    buckets = {cat: [] for cat in KEYWORDS.keys()}

    for url in urls:
        titles = scrape_any_site(url)
        for title in titles:
            lower_title = title.lower()

            # STRICT ROUTING: Check categories in order of priority
            matched = False
            for category in ['CV', 'UNITY', 'AGENT', 'RAG']:
                if any(word in lower_title for word in KEYWORDS[category]):
                    buckets[category].append(f"TOPIC: {title}\nSOURCE: {url}\n\n")
                    matched = True
                    break  # Stop looking after the first match to avoid cluttering other roles

    for category, items in buckets.items():
        send_email(
            os.getenv(f'RECIPIENTS_{category}'),
            category,
            "".join(items),
            ROLES[category]
        )


if __name__ == "__main__":
    job()
