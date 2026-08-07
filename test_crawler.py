import asyncio
import json
import sys
from crawler.fetcher import fetch_page
from crawler.parser import parse_html
from crawler.classifier import classify_and_extract_topics

# The 3 test URLs specified in the BrightEdge Assignment PDF
TEST_URLS = [
    {
        "name": "Amazon Product URL",
        "url": "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"
    },
    {
        "name": "REI Outdoors Blog URL",
        "url": "https://www.rei.com/blog/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/"
    },
    {
        "name": "CNN Tech AI News URL",
        "url": "https://www.cnn.com/2025/09/23/tech/google-study-90-percent-tech-jobs-ai"
    }
]


async def run_test():
    print("=" * 80)
    print(" BRIGHTEDGE WEB CRAWLER - PART 1 TEST SUITE ")
    print("=" * 80)

    for item in TEST_URLS:
        print(f"\n[TESTING] {item['name']}")
        print(f"URL: {item['url']}")
        print("-" * 60)

        # 1. Fetch
        fetch_res = await fetch_page(item['url'])
        print(f"HTTP Status      : {fetch_res.status_code}")
        print(f"Response Time    : {fetch_res.response_time_ms} ms")
        print(f"Content Type     : {fetch_res.content_type}")

        if fetch_res.status_code >= 400 and not fetch_res.raw_html:
            print(f"[ERROR] Fetch failed: {fetch_res.error}")
            continue

        # 2. Parse Metadata
        meta = parse_html(fetch_res.final_url, fetch_res.raw_html)
        print(f"\n--- Extracted Metadata ---")
        print(f"Title            : {meta.title}")
        print(f"Description      : {meta.description[:120] if meta.description else 'N/A'}...")
        print(f"Canonical URL    : {meta.canonical_url}")
        print(f"Language         : {meta.language}")
        print(f"Word Count       : {meta.word_count} words (Est. Read: {meta.estimated_read_time_min} mins)")
        print(f"Links / Images   : {meta.links_count} links / {meta.images_count} images")

        # 3. Classify Page & Topics
        cls = classify_and_extract_topics(
            url=fetch_res.final_url,
            title=meta.title or "",
            description=meta.description or "",
            body_text=meta.body_text_clean or "",
            h1_headings=meta.h1_headings,
            og_metadata=meta.og_metadata
        )

        print(f"\n--- Classification & Topic Extraction ---")
        print(f"Primary Category : {cls.primary_category} (Confidence: {cls.confidence_score * 100:.1f}%)")
        print(f"Top Topics       : {', '.join(cls.topics)}")
        print(f"Entities Detected: {', '.join(cls.entities)}")
        print(f"Content Tags     : {', '.join(cls.content_tags)}")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_test())
