import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- START DATE FILTER ---
START_DATE = datetime(2026, 1, 1)

# --- GLOBAL DUPLICATE PROTECTION ---
SEEN_TITLES = set()

ROLES = {
    'CV': """Expert Prompt: You are a Senior Computer Vision Researcher & Generative Systems Engineer specializing in 2026 Multimodal Architectures.
Scope: Building AI systems that understand images/videos/documents to generate structured JSON data for automation.
Focus: Identify breakthroughs in VLM/MLLM, Scene Graph Generation, Real-time Video Understanding, and Diffusion Models. 
Tech: Python, PyTorch, HuggingFace, Vertex AI, vLLM, and Agentic AI (MCP/API integration, grounding, and hallucination control).""",

    'UNITY': """Expert Prompt: You are a Spatial Computing Architect and Engineer.
Scope: Focus on 3D reconstruction, Guided Data, and high-fidelity environmental digitization for XR and industrial digital twins.
Focus: You look for 2026 developments in Gaussian Splatting, NeRF integration within Unity, Depth sensing, and Point Clouds.""",

    'AGENT': """Expert Prompt: You are an Agentic AI Specialist and Systems Lead.
Scope: Designing and monitoring autonomous Multi-Agent Systems, Swarms, and Agentic workflows.
Focus: 2026 evolution of Planning Agents, recursive reasoning, tool-use proficiency, and agentic orchestration specifically within mobile (iOS/Xcode) and enterprise environments.""",

    'RAG': """Expert Prompt: You are a Data Infrastructure & Integration Engineer focused on the 'Memory Layer' of 2026 AI.
Scope: Design and manage database infrastructure, knowledge graphs, vector stores, and memory systems.
Focus: Analyze developments in GraphRAG, Vector Persistence, and Long-term Agentic Memory (Neo4j, Pinecone) to solve retrieval hallucinations and context window limitations."""
}

KEYWORDS = {
    'CV': [
        'multimodal','vision language model','vlm','mllm','multimodal agent',
        'image understanding','video understanding','scene graph','visual reasoning',
        'generative ai','diffusion model','image generation','multimodal generation',
        'vllm','huggingface transformers','vertex ai','gemini api','open source vlm',
        'agentic ai','tool use','mcp','api integration','routing','grounding',
        'hallucination control','ai evaluation','benchmarking',
        'pytorch','huggingface','multimodal model',
        'new multimodal model','vision language research','ai agent framework',
        'diffusion model update','multimodal tools','openai','google ai',
        'meta ai','anthropic','scalable ai systems'
    ],
    'UNITY': [
        'spatial','3d','guided data','gaussian','nerf','depth','point cloud','unity',
        '3dgs','gaussian splatting','differentiable rendering','radiance fields',
        'volumetric','mesh reconstruction','sub-millimeter precision',
        'xr','mixed reality','spatial computing','digital twin','omniverse',
        'lidar fusion','slam','6dof','point cloud compression',
        'semantic 3d','vision-language 3d','spatial grounding','neural assets',
        'world alignment','dynamic scene synthesis'
    ],
    'AGENT': [
        'multi-agent','swarm','autonomous','xcode','ios','agent workflow',
        'agentic','orchestration','multi-agent systems',
        'recursive reasoning','task decomposition','autonomous planning',
        'mcp','model context protocol','a2a','agent-to-agent','langgraph',
        'crewai','autogen','semantic kernel','agentic state machine',
        'app intents','apple intelligence','on-device agent','swiftui ai',
        'mobile orchestration','local llm agent','xcode ai tools'
    ],
    'RAG': [
        'database','graph','knowledge graph','vector store','vector database',
        'memory system','rag','graphrag','data persistence','retrieval',
        'agent memory','neo4j','pinecone'
    ]
}


def scrape_any_site(url):

    headers = {'User-Agent': 'Mozilla/5.0'}

    try:

        response = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(response.text, 'html.parser')

        titles = []

        for h in soup.find_all(['h1', 'h2', 'h3', 'div'], class_=['list-title', 'title', 'headline']):

            text = h.get_text(strip=True)

            if len(text) > 20:

                # Run script only after 1-1-2026
                if datetime.now() < START_DATE:
                    return []

                normalized = text.lower().strip()

                if normalized in SEEN_TITLES:
                    continue

                SEEN_TITLES.add(normalized)

                titles.append(text)

        print(f"Successfully scraped {len(titles)} potential titles from: {url}")

        return list(set(titles[:10]))

    except Exception as e:

        print(f"Error scraping {url}: {e}")

        return []


def send_email(recipient, subject, content, role_desc):

    if not content.strip() or not recipient:
        print(f"Skipping {subject}: No content or recipient found.")
        return

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

            print(f"✅ Dispatched {subject} to {recipient}")

    except Exception as e:

        print(f"❌ Mail Error for {subject}: {e}")


def job():

    print(f"--- 2026 Research Process Started at {datetime.now()} ---")

    urls = []

    for i in range(1, 6):

        chunk = os.getenv(f'RES_{i}', '')

        if chunk:
            urls.extend([u.strip() for u in chunk.split(',') if u.strip()])

    print(f"Loaded {len(urls)} URLs to process.")

    buckets = {cat: [] for cat in KEYWORDS.keys()}

    bucket_seen = set()

    for url in urls:

        print(f"Processing URL: {url}")

        titles = scrape_any_site(url)

        for title in titles:

            lower_title = title.lower()

            matched = False

            for category in ['CV', 'UNITY', 'AGENT', 'RAG']:

                if any(word in lower_title for word in KEYWORDS[category]):

                    key = title.lower().strip()

                    if key in bucket_seen:
                        continue

                    bucket_seen.add(key)

                    buckets[category].append(f"TOPIC: {title}\nSOURCE: {url}\n\n")

                    print(f"  -> Matched '{title[:50]}...' to Category: {category}")

                    matched = True

                    break

    print("\n--- Summary of Matches ---")

    for cat, items in buckets.items():
        print(f"{cat}: {len(items)} items found.")

    print("\n--- Starting Email Dispatch ---")

    for category, items in buckets.items():

        send_email(
            os.getenv(f'RECIPIENTS_{category}'),
            category,
            "".join(items),
            ROLES[category]
        )

    print(f"--- Job Finished at {datetime.now()} ---")


if __name__ == "__main__":
    job()
