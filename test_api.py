import asyncio
import json
import httpx
from app import app

async def main():
    # Use ASGITransport for modern httpx (>= 0.28.0) compatibility
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("\n================================================================================")
        print(" BRIGHTEDGE WEB CRAWLER - FASTAPI ENDPOINT TEST SUITE ")
        print("================================================================================")
        
        # 1. Health Check Test
        print("\n[TEST 1] GET /api/health")
        res = await client.get("/api/health")
        print(f"Status Code : {res.status_code}")
        print(f"Response    : {res.json()}")

        # 2. Single Crawl Test
        print("\n[TEST 2] POST /api/crawl (Amazon Toaster URL)")
        amazon_url = "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"
        res = await client.post("/api/crawl", json={"url": amazon_url})
        print(f"Status Code : {res.status_code}")
        data = res.json()
        print(f"Success     : {data.get('success')}")
        print(f"Crawl Time  : {data.get('response_time_ms')} ms")
        print(f"Title       : {data.get('metadata', {}).get('title')}")
        print(f"Category    : {data.get('classification', {}).get('primary_category')}")
        print(f"Topics      : {', '.join(data.get('classification', {}).get('topics', []))}")

        # 3. Batch Crawl Test
        print("\n[TEST 3] POST /api/crawl/batch (Multiple URLs)")
        batch_urls = [
            "https://www.cnn.com/2025/09/23/tech/google-study-90-percent-tech-jobs-ai",
            "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"
        ]
        res = await client.post("/api/crawl/batch", json={"urls": batch_urls})
        print(f"Status Code : {res.status_code}")
        batch_data = res.json()
        print(f"Batch Count : {batch_data.get('batch_count')}")
        print(f"Results Rec : {len(batch_data.get('results', []))}")
        for idx, item in enumerate(batch_data.get("results", [])):
            print(f"  Url #{idx+1}   : {item.get('url')} -> Category: {item.get('classification', {}).get('primary_category') if item.get('classification') else 'N/A'}")
        
        print("\n================================================================================")

if __name__ == "__main__":
    asyncio.run(main())

