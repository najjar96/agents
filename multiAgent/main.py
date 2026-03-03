import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- UNIVERSAL SCRAPER ENGINE ---
def scrape_any_site(url):
    """Attempts to find news titles or paper titles on any given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles = []
        # Strategy 1: Look for common research paper tags
        if "arxiv" in url:
            items = soup.find_all('div', class_='list-title')
            titles = [item.get_text(strip=True).replace('Title:', '') for item in items[:5]]
        
        # Strategy 2: Fallback for general news/blogs (Look for H2 and H3 tags)
        if not titles:
            # We take the first 5 headings that look like titles
            headings = soup.find_all(['h2', 'h3', 'h1'])
            for h in headings:
                text = h.get_text(strip=True)
                if len(text) > 20: # Ignore short menu items like "Home" or "Login"
                    titles.append(text)
                if len(titles) >= 5: break
                
        return titles if titles else ["No specific updates found today."]
    except Exception as e:
        return [f"Could not reach site: {str(e)}"]

# --- EMAIL ENGINE ---
def send_email(recipient, subject, content):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not recipient or not sender_email:
        print(f"Skipping email for {subject}: Recipient or Sender missing.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(content, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent: {subject}")
    except Exception as e:
        print(f"Email error: {e}")

# --- MAIN AUTOMATION LOGIC ---
def job():
    print(f"--- Process Started at {datetime.now()} ---")
    
    # 1. Collect all URLs from the 5 Chunks in GitHub Actions
    all_urls = []
    for i in range(1, 6):
        chunk = os.getenv(f'RES_{i}', '')
        if chunk:
            all_urls.extend([u.strip() for u in chunk.split(',') if u.strip()])
    
    print(f"Loaded {len(all_urls)} target resources.")

    # 2. Scrape and Build Report
    full_report = "DAILY AI & RESEARCH MEGA-UPDATE\n" + "="*30 + "\n\n"
    
    for url in all_urls:
        print(f"Scraping: {url}")
        titles = scrape_any_site(url)
        full_report += f"\nSOURCE: {url}\n"
        for t in titles:
            full_report += f"- {t}\n"
        full_report += "-"*20 + "\n"

    # 3. Send to your various engineering groups
    # You can send the full mega-report to everyone, or split it.
    recipients = [
        os.getenv('RECIPIENTS_CV'),
        os.getenv('RECIPIENTS_RAG'),
        os.getenv('RECIPIENTS_UNITY')
    ]
    
    unique_recipients = list(set([r for r in recipients if r]))
    
    for group_email in unique_recipients:
        send_email(group_email, "Daily Mega Research Update", full_report)

if __name__ == "__main__":
    job()
