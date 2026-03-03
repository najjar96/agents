import schedule
import time
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from agents.UnityAgent.UnityAgentTopic import UnityAgent
from agents.computerVisionAgent.computerVisionAgentTopic import CVAgent
from agents.RagAgent.RagAgentTopic import RagAgent

load_dotenv('config.env')


def send_topic_email(recipient_list, topic_name, content):
    if not recipient_list or not content:
        return

    msg = EmailMessage()
    msg['Subject'] = f"Daily Update: {topic_name}"
    msg['From'] = os.getenv('SENDER_EMAIL')

    recipients = [email.strip() for email in recipient_list.split(',')]
    msg['To'] = ", ".join(recipients)
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'))
            smtp.send_message(msg)
        print(f"Sent {topic_name} update to: {msg['To']}")
    except Exception as e:
        print(f"Error sending {topic_name}: {e}")


def job():
    print(f"--- Process Started at {time.ctime()} ---")

    # 1. Scrape data using the agents
    report_cv = CVAgent().get_updates(os.getenv('URL_CV'))
    report_rag = RagAgent().get_updates(os.getenv('URL_RAG'))
    report_unity = UnityAgent().get_updates(os.getenv('URL_3D'))

    # 2. Send customized emails
    # Send CV to eng4
    send_topic_email(os.getenv('RECIPIENTS_CV'), "Computer Vision", report_cv)

    # Send RAG to eng3
    send_topic_email(os.getenv('RECIPIENTS_RAG'), "RAG Topic", report_rag)

    # Send Unity to eng10 and eng9
    send_topic_email(os.getenv('RECIPIENTS_UNITY'), "Unity & 3D", report_unity)


# Schedule for 10:00 AM
schedule.every().day.at("10:00").do(job)

if __name__ == "__main__":
    print("Testing customized email distribution...")
    job()

    print("\nWaiting for 10:00 AM schedule...")
    while True:
        schedule.run_pending()
        time.sleep(60)