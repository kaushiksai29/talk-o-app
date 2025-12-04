import praw
from pymed import PubMed
import feedparser
import json
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit Config
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# PubMed Config
PUBMED_TOOL = "ADHD_Knowledge_Builder"
PUBMED_EMAIL = "youremail@example.com" # Ideally this should also be in env

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "../data/raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed")

def ensure_dirs():
    os.makedirs(f"{RAW_DIR}/reddit", exist_ok=True)
    os.makedirs(f"{RAW_DIR}/blogs", exist_ok=True)
    os.makedirs(f"{RAW_DIR}/research", exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

def fetch_reddit_data():
    print("\n--- Fetching Reddit Data for Sage ---")
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("Skipping Reddit: Credentials not found.")
        return []

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    # Sage focuses on strategies, tips, and productivity, but we also want to cover general ADHD support
    subreddits = [
        "ADHD", "productivity", "getdisciplined", "ADHD_strategies",
        "ADHDWomen", "ADHDers", "ADHDthriving", "ADHD_partners", 
        "AutisticWithADHD", "adhd_anxiety", "AdhdRelationships", 
        "adhdparenting", "ADHD_Programmers", "AdultADHDSupportGroup", 
        "MentalHealthSupport"
    ]
    data = []

    for sub in subreddits:
        print(f"Scraping r/{sub}...")
        try:
            subreddit = reddit.subreddit(sub)
            for post in tqdm(subreddit.hot(limit=50), total=50, desc=f"r/{sub}"):
                if not post.selftext:
                    continue
                
                # For Sage, we want the post content itself if it's a tip, or high quality comments
                # Let's grab the post title and text as a "strategy" context
                data.append({
                    "text": post.selftext,
                    "context": post.title,
                    "source": f"reddit_r/{sub}",
                    "type": "reddit"
                })
                time.sleep(0.5) # Be polite
        except Exception as e:
            print(f"Error scraping r/{sub}: {e}")

    output_path = f"{RAW_DIR}/reddit/sage_reddit.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")
    print(f"Saved {len(data)} Reddit items to {output_path}")
    return data

def fetch_pubmed_data():
    print("\n--- Fetching PubMed Data for Sage ---")
    pubmed = PubMed(tool=PUBMED_TOOL, email=PUBMED_EMAIL)
    query = 'ADHD AND (strategy OR management OR treatment OR "executive function")'
    results = pubmed.query(query, max_results=50)
    articles = []
    
    for article in tqdm(results, desc="PubMed"):
        if article.abstract:
            articles.append({
                "text": article.abstract,
                "context": article.title,
                "source": "pubmed",
                "type": "research"
            })
            
    output_path = f"{RAW_DIR}/research/sage_research.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in articles:
            json.dump(item, f)
            f.write("\n")
    print(f"Saved {len(articles)} PubMed items to {output_path}")
    return articles

def fetch_blog_data():
    print("\n--- Fetching Blog Data for Sage ---")
    feeds = [
        "https://chadd.org/feed/",
        "https://add.org/feed/",
        "https://www.psychologytoday.com/us/blog/adhd-and-me/rss"
    ]
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                articles.append({
                    "text": entry.summary if 'summary' in entry else entry.title,
                    "context": entry.title,
                    "source": url,
                    "type": "blog"
                })
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")

    output_path = f"{RAW_DIR}/blogs/sage_blogs.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in articles:
            json.dump(item, f)
            f.write("\n")
    print(f"Saved {len(articles)} Blog items to {output_path}")
    return articles

def fetch_arxiv_data():
    print("\n--- Fetching ArXiv Data for Sage ---")
    import arxiv
    # Search for ADHD related papers in Quantitative Biology (Neurons and Cognition) or similar
    client = arxiv.Client()
    search = arxiv.Search(
        query = 'abs:ADHD OR abs:"attention deficit" OR abs:"executive function"',
        max_results = 50,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )
    
    articles = []
    try:
        for result in client.results(search):
            articles.append({
                "text": result.summary,
                "context": result.title,
                "source": f"arxiv_{result.entry_id}",
                "type": "research" # or "arxiv" specific type
            })
    except Exception as e:
        print(f"Error fetching ArXiv: {e}")

    output_path = f"{RAW_DIR}/research/sage_arxiv.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in articles:
            json.dump(item, f)
            f.write("\n")
    print(f"Saved {len(articles)} ArXiv items to {output_path}")
    return articles

def process_and_combine():
    print("\n--- Processing and Combining Data ---")
    all_items = []
    
    # Load from raw files
    files = [
        f"{RAW_DIR}/reddit/sage_reddit.jsonl",
        f"{RAW_DIR}/research/sage_research.jsonl",
        f"{RAW_DIR}/research/sage_arxiv.jsonl",
        f"{RAW_DIR}/blogs/sage_blogs.jsonl"
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                        # Standardize for ingestion
                        # Ingestion expects: text, source, persona
                        processed_item = {
                            "text": item.get("text", "") or item.get("abstract", "") or item.get("summary", ""),
                            "context": item.get("context", "") or item.get("title", ""),
                            "source": item.get("source", "unknown"),
                            "persona": "sage"
                        }
                        if processed_item["text"]:
                            all_items.append(processed_item)
                    except json.JSONDecodeError:
                        continue

    output_path = f"{PROCESSED_DIR}/sage_dataset.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in all_items:
            json.dump(item, f)
            f.write("\n")
    print(f"Successfully created {output_path} with {len(all_items)} items.")

if __name__ == "__main__":
    ensure_dirs()
    fetch_reddit_data()
    fetch_pubmed_data()
    fetch_arxiv_data()
    fetch_blog_data()
    process_and_combine()
