import time
import random
import logging
from dataclasses import dataclass
from typing import Optional, Dict
import httpx

logger = logging.getLogger(__name__)

# Pool of modern desktop User-Agents to prevent immediate bot-blocking on public sites
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

@dataclass
class FetchResult:
    url: str
    final_url: str
    status_code: int
    content_type: str
    raw_html: str
    response_time_ms: float
    headers: Dict[str, str]
    error: Optional[str] = None


async def fetch_page(url: str, timeout: float = 15.0) -> FetchResult:
    """
    Fetches raw HTML content for a given URL asynchronously with custom browser headers.
    """
    start_time = time.time()
    user_agent = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            verify=False,  # Fallback for SSL certificates in test environment
            timeout=httpx.Timeout(timeout),
            headers=headers
        ) as client:
            response = await client.get(url)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            
            content_type = response.headers.get("content-type", "")
            return FetchResult(
                url=url,
                final_url=str(response.url),
                status_code=response.status_code,
                content_type=content_type,
                raw_html=response.text,
                response_time_ms=elapsed_ms,
                headers=dict(response.headers),
                error=None if response.is_success else f"HTTP {response.status_code}"
            )

    except httpx.TimeoutException:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return FetchResult(
            url=url,
            final_url=url,
            status_code=504,
            content_type="",
            raw_html="",
            response_time_ms=elapsed_ms,
            headers={},
            error=f"Request timed out after {timeout} seconds"
        )
    except Exception as e:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"Error fetching URL {url}: {str(e)}")
        return FetchResult(
            url=url,
            final_url=url,
            status_code=500,
            content_type="",
            raw_html="",
            response_time_ms=elapsed_ms,
            headers={},
            error=str(e)
        )
