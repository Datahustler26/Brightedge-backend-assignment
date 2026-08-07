import re
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

@dataclass
class MetadataResult:
    url: str
    title: Optional[str]
    description: Optional[str]
    keywords: List[str]
    canonical_url: Optional[str]
    language: Optional[str]
    og_metadata: Dict[str, str]
    twitter_metadata: Dict[str, str]
    h1_headings: List[str]
    h2_headings: List[str]
    h3_headings: List[str]
    body_text_clean: str
    word_count: int
    estimated_read_time_min: float
    meta_robots: Optional[str]
    links_count: int
    images_count: int


def parse_html(url: str, html_content: str) -> MetadataResult:
    """
    Parses raw HTML and extracts key metadata, OpenGraph fields, clean text, JSON-LD, and structure metrics.
    """
    if not html_content or not html_content.strip():
        return MetadataResult(
            url=url, title=None, description=None, keywords=[], canonical_url=None,
            language=None, og_metadata={}, twitter_metadata={}, h1_headings=[],
            h2_headings=[], h3_headings=[], body_text_clean="", word_count=0,
            estimated_read_time_min=0.0, meta_robots=None, links_count=0, images_count=0
        )

    soup = BeautifulSoup(html_content, "lxml")

    # 1. Page Title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    if not title:
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "og:title"})
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
            
    if not title:
        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        if tw_title and tw_title.get("content"):
            title = tw_title["content"].strip()

    if not title:
        h1_first = soup.find("h1")
        if h1_first and h1_first.get_text(strip=True):
            title = h1_first.get_text(strip=True)

    # 2. Meta Description
    description = None
    desc_tag = (
        soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)}) or
        soup.find("meta", property=re.compile(r"^og:description$", re.I)) or
        soup.find("meta", attrs={"name": re.compile(r"^twitter:description$", re.I)})
    )
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"].strip()

    # 3. Meta Keywords
    keywords = []
    kw_tag = soup.find("meta", attrs={"name": re.compile(r"^keywords$", re.I)})
    if kw_tag and kw_tag.get("content"):
        keywords = [k.strip() for k in kw_tag["content"].split(",") if k.strip()]

    # 4. Canonical URL
    canonical_url = None
    canonical_tag = soup.find("link", rel=lambda x: x and "canonical" in x.lower())
    if canonical_tag and canonical_tag.get("href"):
        canonical_url = canonical_tag["href"].strip()

    # 5. Language
    language = None
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        language = html_tag["lang"].strip()

    # 6. OpenGraph Metadata
    og_metadata = {}
    for meta in soup.find_all("meta"):
        prop = meta.get("property") or meta.get("name", "")
        if prop.lower().startswith("og:"):
            val = meta.get("content", "").strip()
            if val:
                og_metadata[prop.lower()] = val

    # 7. Twitter Metadata
    twitter_metadata = {}
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property", "")
        if name.lower().startswith("twitter:"):
            val = meta.get("content", "").strip()
            if val:
                twitter_metadata[name.lower()] = val

    # JSON-LD Schema fallback for Title / Description if missing
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            if script.string:
                ld_data = json.loads(script.string)
                if isinstance(ld_data, dict):
                    if not title and "name" in ld_data:
                        title = str(ld_data["name"])
                    if not title and "headline" in ld_data:
                        title = str(ld_data["headline"])
                    if not description and "description" in ld_data:
                        description = str(ld_data["description"])
        except Exception:
            pass

    # 8. Headings (H1, H2, H3)
    h1_headings = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
    h2_headings = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
    h3_headings = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]

    # 9. Meta Robots
    meta_robots = None
    robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    if robots_tag and robots_tag.get("content"):
        meta_robots = robots_tag["content"].strip()

    # 10. Link and Image counts
    links_count = len(soup.find_all("a", href=True))
    images_count = len(soup.find_all("img"))

    # 11. Extract Clean Body Text
    soup_clean = BeautifulSoup(html_content, "lxml")
    for elem in soup_clean(["script", "style", "nav", "footer", "header", "noscript", "svg", "form", "iframe", "aside"]):
        elem.extract()

    # Remove ad and sponsored elements
    for ad_elem in soup_clean.find_all(class_=re.compile(r"sponsored|ad-slot|ad-container|promotional-banner|cookie", re.I)):
        ad_elem.extract()
    for ad_elem in soup_clean.find_all(id=re.compile(r"sponsored|ad-slot|ad-container", re.I)):
        ad_elem.extract()

    # Find candidates for main content
    content_candidates = []
    
    # Priority containers for e-commerce and articles
    for container_id in ["dp", "centerCol", "productDescription", "feature-bullets", "main-content", "article-content"]:
        matched = soup_clean.find(id=container_id)
        if matched and len(matched.get_text(strip=True)) > 20:
            content_candidates.append(matched)

    main_tag = soup_clean.find("main") or soup_clean.find("article")
    if main_tag and len(main_tag.get_text(strip=True)) > 20:
        content_candidates.append(main_tag)

    for div in soup_clean.find_all("div", class_=re.compile(r"^(content|main-content|post-content|article-body|entry-content|page-content)$", re.I)):
        if len(div.get_text(strip=True)) > 20:
            content_candidates.append(div)

    if not content_candidates:
        content_candidates.append(soup_clean.body or soup_clean)

    # Select the candidate with the highest text length to avoid small boilerplate boxes
    best_candidate = max(content_candidates, key=lambda c: len(c.get_text(strip=True)) if c else 0)
    body_text_raw = best_candidate.get_text(separator=" ", strip=True) if best_candidate else ""
    body_text_clean = re.sub(r"\s+", " ", body_text_raw).strip()

    words = re.findall(r"\b[a-zA-Z0-9]+\b", body_text_clean)
    word_count = len(words)
    estimated_read_time_min = round(word_count / 200.0, 1)

    return MetadataResult(
        url=url,
        title=title,
        description=description,
        keywords=keywords,
        canonical_url=canonical_url,
        language=language,
        og_metadata=og_metadata,
        twitter_metadata=twitter_metadata,
        h1_headings=h1_headings[:5],
        h2_headings=h2_headings[:10],
        h3_headings=h3_headings[:10],
        body_text_clean=body_text_clean[:2000],
        word_count=word_count,
        estimated_read_time_min=estimated_read_time_min,
        meta_robots=meta_robots,
        links_count=links_count,
        images_count=images_count
    )
