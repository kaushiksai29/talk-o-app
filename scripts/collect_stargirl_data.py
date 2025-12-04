# scripts/collect_stargirl_data.py

import praw
import json
import time  # <-- IMPORT TIME
from prawcore.exceptions import TooManyRequests  # <-- IMPORT THE ERROR
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not found in .env file.")
    exit()

if not USER_AGENT or "YOUR_REDDIT_USERNAME_HERE" in USER_AGENT:
    print("Error: Please update the USER_AGENT in your .env file with your Reddit username.")
    print("Example: REDDIT_USER_AGENT=adhd_support_pal_v0.1 by /u/your_username")
    exit()


# Setting up Reddit API
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT  # <-- FIX: Use the USER_AGENT variable you loaded
)

print(f"Successfully connected to Reddit as: {USER_AGENT}")

subreddits = ["ADHD", "ADHDWomen", "ADHDers", "ADHDthriving", "ADHD_partners", "AutisticWithADHD", "adhd_anxiety", "AdhdRelationships", "adhdparenting", "ADHD_Programmers", "AdultADHDSupportGroup", "MentalHealthSupport"]

data = []
total_posts_processed = 0

def fetch_reddit_posts():
    global total_posts_processed # Use global to update the counter
    for sub in subreddits:
        print(f"\n--- Scraping subreddit: r/{sub} ---")
        try:
            subreddit = reddit.subreddit(sub)
            
            # Wrap the post iteration in tqdm for a progress bar
            # We use 'total' to give tqdm an idea of the max limit
            for post in tqdm(subreddit.hot(limit=200), total=200, desc=f"r/{sub}"):
                try:
                    # --- This is the "expensive" block that needs error handling ---
                    
                    # Skip posts without text
                    if not post.selftext or post.selftext == "[deleted]" or post.selftext == "[removed]":
                        continue

                    post.comments.replace_more(limit=0)
                    
                    for comment in post.comments.list():
                        if (comment.body and 
                            len(comment.body.split()) > 10 and 
                            not comment.is_submitter and
                            comment.body != "[deleted]" and
                            comment.body != "[removed]"):
                            
                            data.append({
                                "context": post.title + "\n\n" + post.selftext, # Get full post text
                                "response": comment.body,
                                "persona": "stargirl",
                                "source": sub
                            })
                    
                    total_posts_processed += 1
                    
                    # --- Proactive Sleep ---
                    # Be a polite API citizen: pause after each post
                    time.sleep(1) 

                except TooManyRequests:
                    # --- Reactive Error Handling ---
                    # We hit a rate limit! Pause for 1 minute.
                    print(f"\n[Rate Limit Hit] Pausing for 60 seconds... (Processed {total_posts_processed} posts)")
                    time.sleep(60)
                    print("[Resuming scrape...]")
                    continue # Skip to the next post
                
                except Exception as e:
                    # Catch other potential errors for a single post
                    print(f"\n[Error processing post {post.id}] Skipping. Error: {e}")
                    continue
        
        except Exception as e:
            # Catch errors related to accessing a subreddit (e.g., private)
            print(f"\n[Major Error] Could not access subreddit r/{sub}. Skipping. Error: {e}")
            continue

if __name__ == "__main__":
    fetch_reddit_posts()
    
    # Ensure the directory exists
    output_dir = "../data/raw/reddit"
    output_file = f"{output_dir}/stargirl_reddit.jsonl"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n--- Writing data to file: {output_file} ---")
    
    with open(output_file, "w", encoding="utf-8") as f:
        for d in data:
            json.dump(d, f)
            f.write("\n")
            
    print(f"\n--- Scraping Complete! ---")
    print(f"Collected {len(data)} empathetic Reddit comments from {total_posts_processed} posts.")