import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION & KEYWORDS ---
KEYWORDS = {
    'RAG': ['vision', 'vlm', 'gen ai', 'generative ai', 'llm', 'diffusion'],
    'UNITY': ['spatial', '3d', 'guided data', 'conditional', 'unity', 'depth', 'gaussian splatting'],
    'CV': ['mcp', 'memory', 'rag', 'retrieval', 'knowledge graph', 'context'],
    'AGENT': ['agent', 'multi-agent', 'autonomous', 'workflow', 'swarm']
}

def scrape_any_site(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = []
        # General scraper for headings
        for h in soup.find_all(['h2', 'h3', 'h1', 'div'], class_=['list-title', 'title']):
            text = h.get_text(strip=True)
            if len(text) > 20:
                titles.append(text)
        return list(set(titles[:10])) # Unique top 10
    except:
        return []

def send_email(recipient, subject, content):
    if not content.strip() or not recipient: return
    sender = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    msg = MIMEMultipart()
    msg['Subject'] = f"{subject} - {datetime.now().strftime('%Y-%m-%d')}"
    msg.attach(MIMEText(content, 'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient.split(','), msg.as_string())
            print(f"Sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")

def job():
    # Collect all URLs from chunks
    urls = []
    for i in range(1, 6):
        chunk = os.getenv(f'RES_{i}', '')
        if chunk: urls.extend([u.strip() for u in chunk.split(',') if u.strip()])

    # Storage for sorted results
    buckets = {'RAG': [], 'UNITY': [], 'CV': [], 'AGENT': []}

    for url in urls:
        print(f"Checking: {url}")
        titles = scrape_any_site(url)
        for title in titles:
            lower_title = title.lower()
            # Routing Logic
            for category, words in KEYWORDS.items():
                if any(w in lower_title for w in words):
                    buckets[category].append(f"- {title}\n  Source: {url}\n")

    # Send specialized emails
    send_email(os.getenv('RECIPIENTS_RAG'), "Vision/VLM/GenAI Update", "".join(buckets['RAG']))
    send_email(os.getenv('RECIPIENTS_UNITY'), "Spatial & Conditional Data Update", "".join(buckets['UNITY']))
    send_email(os.getenv('RECIPIENTS_CV'), "MCP/Memory/RAG Update", "".join(buckets['CV']))
    send_email(os.getenv('RECIPIENTS_AGENT'), "AI Agents & Autonomous Systems", "".join(buckets['AGENT']))

if __name__ == "__main__":
    job()
