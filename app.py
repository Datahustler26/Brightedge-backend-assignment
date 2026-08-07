import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from crawler.fetcher import fetch_page
from crawler.parser import parse_html
from crawler.classifier import classify_and_extract_topics

app = FastAPI(
    title="BrightEdge Web Scale Crawler Engine",
    description="High-performance web crawler, HTML metadata extractor, page classifier, and topic analysis engine.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class CrawlRequest(BaseModel):
    url: str

class BatchCrawlRequest(BaseModel):
    urls: List[str]


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "brightedge-crawler-engine",
        "version": "1.0.0"
    }


@app.post("/api/crawl")
async def crawl_single_url(req: CrawlRequest):
    """
    Crawls a single URL, extracts HTML metadata, classifies page category, and returns topic analysis.
    """
    url = req.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Step 1: Fetch raw HTML content
    fetch_res = await fetch_page(url)

    # Handle fetch failure
    if fetch_res.status_code >= 400 and not fetch_res.raw_html:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "url": url,
                "status_code": fetch_res.status_code,
                "error": fetch_res.error or f"HTTP error {fetch_res.status_code}",
                "response_time_ms": fetch_res.response_time_ms,
                "metadata": None,
                "classification": None
            }
        )

    # Step 2: Extract HTML Metadata
    metadata = parse_html(fetch_res.final_url, fetch_res.raw_html)

    # Step 3: Classify Page & Extract Topics
    classification = classify_and_extract_topics(
        url=fetch_res.final_url,
        title=metadata.title or "",
        description=metadata.description or "",
        body_text=metadata.body_text_clean or "",
        h1_headings=metadata.h1_headings,
        og_metadata=metadata.og_metadata
    )

    return {
        "success": True,
        "url": fetch_res.url,
        "final_url": fetch_res.final_url,
        "status_code": fetch_res.status_code,
        "content_type": fetch_res.content_type,
        "response_time_ms": fetch_res.response_time_ms,
        "metadata": {
            "title": metadata.title,
            "description": metadata.description,
            "keywords": metadata.keywords,
            "canonical_url": metadata.canonical_url,
            "language": metadata.language,
            "og_metadata": metadata.og_metadata,
            "twitter_metadata": metadata.twitter_metadata,
            "h1_headings": metadata.h1_headings,
            "h2_headings": metadata.h2_headings,
            "h3_headings": metadata.h3_headings,
            "body_snippet": metadata.body_text_clean[:600],
            "word_count": metadata.word_count,
            "estimated_read_time_min": metadata.estimated_read_time_min,
            "meta_robots": metadata.meta_robots,
            "links_count": metadata.links_count,
            "images_count": metadata.images_count,
        },
        "classification": {
            "primary_category": classification.primary_category,
            "confidence_score": classification.confidence_score,
            "topics": classification.topics,
            "entities": classification.entities,
            "content_tags": classification.content_tags
        }
    }


@app.post("/api/crawl/batch")
async def crawl_batch_urls(req: BatchCrawlRequest):
    """
    Crawls a batch of URLs concurrently with semaphore concurrency control.
    """
    urls = req.urls
    if not urls:
        raise HTTPException(status_code=400, detail="URL list cannot be empty")

    if len(urls) > 20:
        raise HTTPException(status_code=400, detail="Maximum batch limit for demo is 20 URLs")

    semaphore = asyncio.Semaphore(5)

    async def crawl_with_limit(url: str):
        async with semaphore:
            req_obj = CrawlRequest(url=url)
            return await crawl_single_url(req_obj)

    tasks = [crawl_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    formatted_results = []
    for res in results:
        if isinstance(res, Exception):
            formatted_results.append({"success": False, "error": str(res)})
        else:
            formatted_results.append(res)

    return {
        "batch_count": len(urls),
        "results": formatted_results
    }


# Serve static directory for frontend web dashboard UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
