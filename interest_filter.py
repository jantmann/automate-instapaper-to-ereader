import os
from sentence_transformers import SentenceTransformer, util

# Load model once at module level so it isn't reloaded for every article
model = SentenceTransformer("all-MiniLM-L6-v2")

# Strict threshold -- only articles with high semantic similarity are sent
SIMILARITY_THRESHOLD = 0.4

def is_article_interesting(title, abstract):
    
    interests = os.getenv("USER_INTERESTS", "")
    description = os.getenv("USER_INTERESTS_DESCRIPTION", "")
    
    # Combine interests and description into one interest profile
    interest_profile = f"{interests}. {description}".strip(". ")
    
    if not interest_profile:
        print("No interests defined in config.env — sending all articles.")
        return True
    
    article_text = f"{title}. {abstract}".strip(". ")
    
    article_embedding = model.encode(article_text, convert_to_tensor=True)
    interest_embedding = model.encode(interest_profile, convert_to_tensor=True)
    
    similarity = util.cos_sim(article_embedding, interest_embedding).item()
    print(f"  Similarity {similarity:.2f} | {title}")
    
    return similarity >= SIMILARITY_THRESHOLD