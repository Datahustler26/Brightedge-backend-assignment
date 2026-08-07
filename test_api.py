import asyncio
import json
import httpx
from app import app

async def main():
    # Use ASGITransport for modern httpx (>= 0.28.0) compatibility
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("\n--- Testing GET /api/health ---")
        res = await client.get("/api/health")
        print("Health Status:", res.status_code, res.json())

        print("\n--- Testing POST /api/crawl with Amazon Toaster URL ---")
        amazon_url = "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster"
        res = await client.post("/api/crawl", json={"url": amazon_url})
        print("API Status Code:", res.status_code)
        data = res.json()
        print("Success:", data.get("success"))
        print("Crawl Time:", data.get("response_time_ms"), "ms")
        print("Category:", data.get("classification", {}).get("primary_category"))
        print("Topics:", data.get("classification", {}).get("topics"))
        print("Title:", data.get("metadata", {}).get("title"))

if __name__ == "__main__":
    asyncio.run(main())
