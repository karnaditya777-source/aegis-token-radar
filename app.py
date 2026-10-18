"""
FastAPI Server for Real-Time Crypto Token Risk & Rug Pull Detector.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import Optional

from core.scanner import TokenScanner
from core.detector import TokenDetector
from core.config import SUPPORTED_CHAINS
from core.mock_scams import DEMO_CASE_STUDIES

scanner = TokenScanner()
detector = TokenDetector(scanner)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background token launch detection
    await detector.start()
    yield
    # Shutdown: Clean up background tasks and HTTP sessions
    await detector.stop()
    await scanner.close()

app = FastAPI(
    title="Crypto Token Risk & Rug Pull Radar",
    description="Automated real-time scanner for newly launched cryptocurrency tokens and risk evaluation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/robots.txt", response_class=PlainTextResponse)
async def serve_robots():
    return """User-agent: *
Allow: /
Allow: /static/
Disallow: /api/demo/

Sitemap: https://aegis-token-radar.vercel.app/sitemap.xml
"""

@app.get("/sitemap.xml")
async def serve_sitemap():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://aegis-token-radar.vercel.app/</loc>
    <lastmod>2026-10-18</lastmod>
    <changefreq>always</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://aegis-token-radar.vercel.app/api/tokens/latest</loc>
    <changefreq>always</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    return Response(content=xml_content, media_type="application/xml")

@app.get("/api/tokens/latest")
async def get_latest_tokens(
    chain: Optional[str] = Query(None, description="Chain filter: solana, ethereum, bsc, base, or all"),
    risk_category: Optional[str] = Query(None, description="Risk category: safe, speculative, high_risk, extreme_risk, or all"),
    min_liquidity: float = Query(0.0, description="Minimum liquidity in USD"),
    q: Optional[str] = Query(None, description="Search query by name, symbol, or address"),
    limit: int = Query(50, description="Max number of tokens to return")
):
    # On serverless platforms like Vercel, poll on-demand if cache is empty
    if len(detector.detected_tokens) <= 4:
        try:
            await detector._poll_latest_launches()
        except Exception as e:
            pass

    tokens = detector.get_detected_tokens(
        chain=chain,
        risk_category=risk_category,
        min_liquidity=min_liquidity,
        search_query=q,
        limit=limit
    )
    return {
        "count": len(tokens),
        "tokens": tokens
    }

@app.get("/api/tokens/scan")
async def scan_single_token(
    address: str = Query(..., description="Token contract address or mint"),
    chain: Optional[str] = Query(None, description="Optional chain hint (solana, ethereum, bsc, base)")
):
    """Deep scan and analyze ANY token contract on demand."""
    clean_addr = address.strip()
    if not clean_addr:
        raise HTTPException(status_code=400, detail="Token address is required")

    result = await scanner.scan_token(clean_addr, chain)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Token '{clean_addr}' could not be located on decentralized exchanges. Verify the contract address and liquidity pool."
        )

    return result

@app.get("/api/stats")
async def get_radar_stats():
    """System real-time radar stats."""
    return {
        "status": "online",
        "detector_active": detector.is_running,
        "stats": detector.stats,
        "supported_chains": list(SUPPORTED_CHAINS.keys())
    }

@app.get("/api/demo/samples")
async def get_demo_samples():
    """Return pre-configured educational case studies (Honeypot, Unlocked Rug, Safe Gem, Degen Meme)."""
    return {
        "samples": [
            {
                "id": d["id"],
                "title": d["title"],
                "chain": d["chain"],
                "symbol": d["market_data"]["symbol"],
                "name": d["market_data"]["name"],
                "address": d["market_data"]["base_token_address"]
            }
            for d in DEMO_CASE_STUDIES
        ]
    }

@app.get("/api/chains")
async def get_supported_chains():
    """List of supported blockchain networks."""
    return SUPPORTED_CHAINS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
