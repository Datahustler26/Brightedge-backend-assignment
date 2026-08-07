import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import Counter
from urllib.parse import urlparse

# Standard English stopwords
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he",
    "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves", "com", "org", "http", "https", "www", "ref", "dp", "qid",
    "sr", "ie", "utf8", "page", "site", "website", "read", "share", "click", "view", "link", "new", "get", "one",
    "two", "use", "make", "way", "first", "also", "time", "day", "people", "like"
}

@dataclass
class ClassificationResult:
    primary_category: str
    confidence_score: float
    topics: List[str]
    entities: List[str]
    content_tags: List[str]


def classify_and_extract_topics(
    url: str,
    title: str = "",
    description: str = "",
    body_text: str = "",
    h1_headings: List[str] = None,
    og_metadata: Dict[str, str] = None
) -> ClassificationResult:
    """
    Classifies page content into generic categories and extracts top topics & entities.
    """
    title = title or ""
    description = description or ""
    body_text = body_text or ""
    h1_headings = h1_headings or []
    og_metadata = og_metadata or {}

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()

    full_corpus = f"{title} {description} {' '.join(h1_headings)} {body_text}"
    lower_corpus = full_corpus.lower()

    # 1. Page Category Detection Heuristics
    category_scores = {
        "E-Commerce Product Page": 0,
        "Blog / Editorial Article": 0,
        "News Article": 0,
        "Technology / AI Report": 0,
        "Outdoors & Recreation": 0,
        "General Informational": 1
    }

    # Signal 1: URL & Domain patterns
    if "amazon.com" in domain or "/dp/" in path or "/product/" in path or "buy" in path:
        category_scores["E-Commerce Product Page"] += 8
    if "walmart.com" in domain or "bestbuy.com" in domain or "ebay.com" in domain:
        category_scores["E-Commerce Product Page"] += 8

    if "blog." in domain or "/blog/" in path or "/camp/" in path or "/guide/" in path:
        category_scores["Blog / Editorial Article"] += 6

    if "cnn.com" in domain or "bbc.com" in domain or "reuters.com" in domain or "/tech/" in path or "/news/" in path:
        category_scores["News Article"] += 6

    # Signal 2: OpenGraph Types
    og_type = og_metadata.get("og:type", "").lower()
    if "product" in og_type or "og:product" in og_metadata:
        category_scores["E-Commerce Product Page"] += 5
    elif "article" in og_type:
        category_scores["Blog / Editorial Article"] += 4

    # Signal 3: Content Keyword matching (generic e-commerce, blog, news, tech indicators)
    ecommerce_keywords = ["price", "add to cart", "customer reviews", "ratings", "prime", "shipping", "in stock", "sku", "specs", "specifications", "description", "checkout", "buy now", "discount", "order"]
    blog_keywords = ["how to", "guide", "tips", "tutorial", "advice", "overview", "introduction", "journey", "story", "experience", "best practices", "ideas", "step by step"]
    news_keywords = ["report", "study", "breaking news", "journalism", "press release", "published", "according to", "spokesperson", "interview", "analysis", "coverage", "survey", "percent", "ai", "tech"]

    for kw in ecommerce_keywords:
        if kw in lower_corpus:
            category_scores["E-Commerce Product Page"] += 1.5

    for kw in blog_keywords:
        if kw in lower_corpus:
            category_scores["Blog / Editorial Article"] += 1.5

    for kw in news_keywords:
        if kw in lower_corpus:
            category_scores["News Article"] += 1.2
            if kw in ["ai", "tech", "study", "report"]:
                category_scores["Technology / AI Report"] += 1.5

    # Determine Winning Category
    winning_category = max(category_scores, key=category_scores.get)
    max_score = category_scores[winning_category]
    confidence = min(0.98, round(max_score / (max_score + 5.0), 2)) if max_score > 1 else 0.50

    # 2. Topic & Keyphrase Extraction using TF-IDF style frequency analysis
    # Extract terms from URL path, Title, Headings, and Body
    url_terms = [t for t in re.split(r"[\/\-\_\.\?\=\&]", path) if len(t) > 2 and t not in STOPWORDS]
    corpus_words = re.findall(r"\b[a-zA-Z]{3,20}\b", full_corpus)
    filtered_words = [w.capitalize() for w in corpus_words if w.lower() not in STOPWORDS]

    # Word Frequency calculation with weighting (Title & Headings get 3x weight)
    weighted_counter = Counter()
    for word in filtered_words:
        weighted_counter[word] += 1

    # Boost words present in title or H1s
    title_words = [w.capitalize() for w in re.findall(r"\b[a-zA-Z]{3,20}\b", title) if w.lower() not in STOPWORDS]
    for tw in title_words:
        weighted_counter[tw] += 4

    for ut in url_terms:
        weighted_counter[ut.capitalize()] += 3

    # Extract top 8 relevant topics
    top_topics = [item[0] for item in weighted_counter.most_common(12)]

    # 3. Dynamic Entity Extraction (Proper Nouns & Organization/Product names from Title & Corpus)
    capitalized_entities = set(re.findall(r"\b[A-Z][a-zA-Z0-9]{1,15}\b", title))
    capitalized_entities.update(re.findall(r"\b[A-Z][a-zA-Z0-9]{1,15}(?:\s+[A-Z][a-zA-Z0-9]{1,15})?\b", " ".join(h1_headings)))
    
    # Filter out common capitalized words that match stopwords
    detected_entities = [ent for ent in capitalized_entities if ent.lower() not in STOPWORDS and len(ent) > 2][:6]

    # Fallback to title keywords if no capitalized entities detected
    if not detected_entities and title_words:
        detected_entities = title_words[:3]

    # 4. Content Tags
    tags = [winning_category]
    if "E-Commerce" in winning_category:
        tags.extend(["Product Page", "Retail", "Shopping"])
    elif "Blog" in winning_category:
        tags.extend(["Editorial", "Guides & Tips", "Lifestyle"])
    elif "News" in winning_category or "Tech" in winning_category:
        tags.extend(["Journalism", "Technology", "Market Analysis"])

    for topic in top_topics[:3]:
        if topic not in tags:
            tags.append(topic)

    return ClassificationResult(
        primary_category=winning_category,
        confidence_score=confidence,
        topics=top_topics[:8],
        entities=detected_entities,
        content_tags=tags[:6]
    )
