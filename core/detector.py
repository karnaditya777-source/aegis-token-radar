"""
Token Launch Detector: Continuously monitors DEX creation feeds (DexScreener, GeckoTerminal)
to detect newly launched tokens as soon as they hit the market and immediately analyzes them.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from core.scanner import TokenScanner
from core.mock_scams import DEMO_CASE_STUDIES
from core.config import GECKOTERMINAL_NEW_POOLS_URL
import aiohttp

class TokenDetector:
    def __init__(self, scanner: TokenScanner):
        self.scanner = scanner
        self.detected_tokens: List[Dict[str, Any]] = []
        self.seen_addresses: set = set()
        self.is_running = False
        self._bg_task: Optional[asyncio.Task] = None
        self.stats = {
            "total_detected": 0,
            "scams_caught": 0,
            "safe_gems_found": 0,
            "speculative_count": 0,
            "started_at": time.time()
        }
        # Prepopulate with demo case studies for instant richness
        self._bootstrap_initial_tokens()

    def _bootstrap_initial_tokens(self):
        """Seed detector with demonstration case studies so user has instant data."""
        for demo in DEMO_CASE_STUDIES:
            risk_eval = self.scanner.risk_engine.evaluate(demo["market_data"], demo["security_data"])
            pot_eval = self.scanner.potential_engine.evaluate(demo["market_data"], risk_eval["score"])
            entry = {
                "token_address": demo["market_data"]["base_token_address"],
                "chain": demo["chain"],
                "market": demo["market_data"],
                "security": demo["security_data"],
                "risk": risk_eval,
                "potential": pot_eval,
                "detected_at": time.time(),
                "is_demo": True,
                "demo_title": demo["title"]
            }
            self.detected_tokens.append(entry)
            self.seen_addresses.add(demo["market_data"]["base_token_address"])
            self._update_stats(risk_eval["risk_category"])

    def _update_stats(self, category: str):
        self.stats["total_detected"] += 1
        if category in ["extreme_risk", "high_risk"]:
            self.stats["scams_caught"] += 1
        elif category == "safe":
            self.stats["safe_gems_found"] += 1
        else:
            self.stats["speculative_count"] += 1

    async def start(self):
        """Start the background token launch detector."""
        if self.is_running:
            return
        self.is_running = True
        self._bg_task = asyncio.create_task(self._detector_loop())
        print("[TokenDetector] Live token launch detection loop started.")

    async def stop(self):
        self.is_running = False
        if self._bg_task:
            self._bg_task.cancel()

    async def _detector_loop(self):
        """Poll new pool creation endpoints periodically."""
        # Initial poll immediately
        await self._poll_latest_launches()
        
        while self.is_running:
            try:
                await asyncio.sleep(20)  # Check every 20 seconds
                await self._poll_latest_launches()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[TokenDetector] Error in detector loop: {e}")
                await asyncio.sleep(10)

    async def _poll_latest_launches(self):
        """Discover new tokens from DexScreener profiles & GeckoTerminal."""
        discovered_candidates: List[Dict[str, str]] = []

        # 1. Fetch from DexScreener latest profiles
        try:
            profiles = await self.scanner.dexscreener.fetch_latest_profiles()
            for p in profiles[:15]:
                addr = p.get("tokenAddress")
                chain = p.get("chainId", "unknown")
                if addr and addr not in self.seen_addresses:
                    discovered_candidates.append({"address": addr, "chain": chain})
        except Exception as e:
            print(f"[TokenDetector] Error fetching DexScreener profiles: {e}")

        # 2. Fetch from GeckoTerminal new pools
        try:
            headers = {"Accept": "application/json;version=20230302"}
            session = await self.scanner.dexscreener.get_session()
            async with session.get(GECKOTERMINAL_NEW_POOLS_URL, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pools = data.get("data", [])
                    for pool in pools[:10]:
                        rel = pool.get("relationships", {})
                        base_token_data = (rel.get("base_token", {}) or {}).get("data", {})
                        token_id = base_token_data.get("id", "")
                        # GeckoTerminal format: network_address, e.g. bsc_0x910...
                        if "_" in token_id:
                            net, addr = token_id.split("_", 1)
                            if addr and addr not in self.seen_addresses:
                                discovered_candidates.append({"address": addr, "chain": net})
        except Exception as e:
            print(f"[TokenDetector] Error fetching GeckoTerminal pools: {e}")

        # Scan new candidates (limit concurrency to 4 at a time to be courteous to APIs)
        for candidate in discovered_candidates[:6]:
            addr = candidate["address"]
            chain = candidate["chain"]
            if addr in self.seen_addresses:
                continue
            
            self.seen_addresses.add(addr)
            try:
                analysis = await self.scanner.scan_token(addr, chain)
                if analysis:
                    analysis["detected_at"] = time.time()
                    # Prepend to detected tokens
                    self.detected_tokens.insert(0, analysis)
                    # Keep max 50 tokens in active feed
                    if len(self.detected_tokens) > 50:
                        self.detected_tokens.pop()
                    
                    self._update_stats(analysis["risk"]["risk_category"])
                    print(f"[TokenDetector] Detected & Audited: {analysis['market'].get('symbol')} on {analysis.get('chain')} | Score: {analysis['risk']['score']}/100")
            except Exception as e:
                print(f"[TokenDetector] Error scanning {addr}: {e}")

    def get_detected_tokens(
        self,
        chain: Optional[str] = None,
        risk_category: Optional[str] = None,
        min_liquidity: float = 0.0,
        search_query: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Filter detected tokens according to user parameters."""
        results = []
        for t in self.detected_tokens:
            # Chain filter
            if chain and chain.lower() != "all":
                token_chain = t.get("chain", "").lower()
                if chain.lower() not in token_chain:
                    continue

            # Risk category filter
            if risk_category and risk_category.lower() != "all":
                if t.get("risk", {}).get("risk_category") != risk_category.lower():
                    continue

            # Liquidity filter
            liq = float(t.get("market", {}).get("liquidity_usd", 0) or 0)
            if liq < min_liquidity:
                continue

            # Search query filter (symbol, name, or address)
            if search_query:
                q = search_query.lower().strip()
                name = (t.get("market", {}).get("name", "")).lower()
                sym = (t.get("market", {}).get("symbol", "")).lower()
                addr = (t.get("token_address", "")).lower()
                if q not in name and q not in sym and q not in addr:
                    continue

            results.append(t)
            if len(results) >= limit:
                break

        return results
