import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- ROLES AND CONSTRAINTS ---
# Only titles containing '2026' or '2027' will be accepted to ensure freshness.
YEAR_CONSTRAINT = ["2026", "2027"]

# Define the "Expert Role" for each category
ROLES = {
    'RAG': "Vision/VLM/GenAI Researcher (Focus: Generative models & Vision-Language)",
    'UNITY': "Spatial Computing Engineer (Focus: 3D, Guided Data, Depth)",
    'CV': "System Architect (Focus: MCP, Memory, RAG for CV)",
    'AGENT': "Agentic AI Specialist (Focus: Autonomous Multi-Agent Systems)"
}

KEYWORDS = {
    'RAG': ['vision', 'vlm', 'gen ai', 'generative ai', 'diffusion', 'multimodal'],
    'UNITY': ['spatial', '3d', 'guided data', 'conditional', 'unity', 'gaussian', 'nerf'],
    'CV': ['mcp', 'memory', 'rag', 'retrieval', 'context window', 'long-term memory'],
    'AGENT': ['agent', 'multi-agent', 'autonomous', 'swarm', 'mcp agent', 'tool-use', 'ios', 'xcode']
}

def is_recent(text):
    """Constraint: Returns True if the text mentions 2026+ or lacks a date (assuming current)."""
    # Many titles don't have the year in them, so we also check the site content
    return any(year in text for year in YEAR_CONSTRAINT)

def scrape_any_site(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = []
        
        # Look for headers and list items
        for h in soup.find_all(['h1', 'h2', 'h3', 'div'], class_=['list-title', 'title', 'headline']):
            text = h.get_text(strip=True)
            # Filter: Must be long enough and MUST be from 2026 if a year is mentioned
            if len(text) > 20:
                # If a year is mentioned, it MUST be 2026 or newer
                years_found = [y for y in ["2023", "2024", "2025"] if y in text]
                if not years_found: # If no old year is found, we assume it's new
                    titles.append(text)
        return list(set(titles[:15]))
    except:
        return []

def send_email(recipient, subject, content, role_desc):
    if not content.strip() or not recipient: return
    sender = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    
    # Prepend the Role and Constraints to the email
    header = f"ROLE: {role_desc}\nCONSTRAINT: Researching only 2026+ data.\n"
    header += "="*50 + "\n\n"
    
    msg = MIMEMultipart()
    msg['Subject'] = f"2026 {subject} Intelligence Report"
    msg.attach(MIMEText(header + content, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient.split(','), msg.as_string())
            print(f"Sent {subject} to {recipient}")
    except Exception as e:
        print(f"Email error: {e}")

def job():
    print(f"--- 2026 Research Process Started ---")
    
    # Collect all URLs from chunks
    urls = []
    for i in range(1, 6):
        chunk = os.getenv(f'RES_{i}', '')
        if chunk: urls.extend([u.strip() for u in chunk.split(',') if u.strip()])

    buckets = {cat: [] for cat in KEYWORDS.keys()}

    for url in urls:
        titles = scrape_any_site(url)
        for title in titles:
            lower_title = title.lower()
            for category, words in KEYWORDS.items():
                if any(w in lower_title for w in words):
                    buckets[category].append(f"TITLE: {title}\nLINK: {url}\n")

    # Send categorized emails with Role Header
    for category in buckets:
        send_email(
            os.getenv(f'RECIPIENTS_{category}'), 
            category, 
            "".join(buckets[category]),
            ROLES[category]
        )

if __name__ == "__main__":
    job()
