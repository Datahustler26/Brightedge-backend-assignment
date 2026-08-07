# BrightEdge Engineering Candidate Assignment - Scale

> **Position**: Software Engineer (Scale / Backend)  
> **Repository**: [Brightedge-backend-assignment](https://github.com/Datahustler26/Brightedge-backend-assignment)  
> **Scope**: Part 1 (Core Crawler, Metadata Extractor & Web Dashboard) & Part 2 (Distributed Web Scale System Design for Billions of URLs per Month).

---

## 🌟 Solution Highlights

- 🕷️ **Generic Async Web Crawler**: Built with Python 3.11, FastAPI, `httpx`, and `BeautifulSoup4` + `lxml`.
- 🏷️ **Metadata & Topic Extractor**: Extracts Title, Description, Meta Keywords, Canonical URL, Language, OpenGraph (`og:*`), Twitter Cards (`twitter:*`), H1-H3 headings, word count, read time, and main clean body content.
- 🧠 **NLP Page Classification**: Classifies pages (`E-Commerce Product Page`, `Blog / Editorial Article`, `News Article`, `Documentation`) and identifies top topics and brand/product entities.
- 🎨 **Glassmorphic Web Dashboard**: Live web dashboard UI (`http://127.0.0.1:8000`) with instant test buttons for assignment URLs (Amazon Toaster, REI Blog, CNN Tech).
- 🏗️ **Billions-Scale System Design ([SYSTEM_DESIGN.md](SYSTEM_DESIGN.md))**:
  - **6 Mermaid Flow Diagrams** (Ingestion, Deduplication, Distributed Crawler Cluster, Storage Tiering, Monitoring).
  - **Unified Schemas**: ClickHouse Relational SQL DDL, NoSQL Document JSON, Apache Parquet Data Lake.
  - **SLOs & SLAs**: 99.9% Uptime, P95 < 2.0s Crawl Latency, 99.999999999% Data Durability.
  - **Cost Optimizations**: **80% storage savings** ($3,600+/mo savings on S3 via Parquet ZSTD) and **70% compute savings** (AWS Spot instances).

---

## 📂 Project Structure

```text
├── app.py                   # FastAPI Application Server (REST API + Web UI)
├── crawler/
│   ├── __init__.py          # Package Init
│   ├── fetcher.py           # Async HTTP fetcher with User-Agent rotation
│   ├── parser.py            # DOM Parser & HTML Metadata extractor
│   └── classifier.py        # Page Classifier & Topic Extraction engine
├── static/
│   └── index.html           # Modern Glassmorphic Web Dashboard UI
├── SYSTEM_DESIGN.md         # Part 2 System Design Document (5B URLs/mo architecture)
├── test_crawler.py          # Standalone CLI Test Suite
├── test_api.py              # API Endpoint Test Suite
├── requirements.txt         # Dependencies
└── README.md                # Project README
```

---

## 🚀 Quick Start & Local Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run CLI Test Suite
```bash
python test_crawler.py
```

### 3. Launch Web Dashboard & API Server
```bash
python app.py
```
Open **`http://127.0.0.1:8000`** in your browser to test the interactive dashboard.

---

## 📊 Sample Crawl Output (Amazon Product Page Test)

```json
{
  "success": true,
  "url": "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C",
  "status_code": 200,
  "response_time_ms": 1945.2,
  "classification": {
    "primary_category": "E-Commerce Product Page",
    "confidence_score": 0.79,
    "topics": ["Kitchen", "Slice", "Toaster", "Home", "Cuisinart", "Compact", "Shade"],
    "entities": ["Amazon", "Cuisinart", "Toaster", "Kitchen"],
    "content_tags": ["E-Commerce Product Page", "Product Page", "Retail", "Shopping"]
  },
  "metadata": {
    "title": "Amazon.com: Cuisinart CPT-122 2-Slice Compact Plastic Toaster...",
    "canonical_url": "https://www.amazon.com/Cuisinart-CPT-122-2-Slice-Compact-Plastic/dp/B009GQ034C",
    "word_count": 9000,
    "estimated_read_time_min": 45.0
  }
}
```

---

## 📘 System Architecture Document

For full Part 2 system design documentation, flowcharts, data schemas, SLO/SLA definitions, Prometheus metrics, and cost optimization calculations, see:  
👉 **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)**
