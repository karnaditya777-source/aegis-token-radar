"""
DexScreener API integration for token pairs, liquidity, volume, transactions, and socials.
"""

import aiohttp
import asyncio
import time
from typing import Dict, Any, Optional, List
from core.config import DEXSCREENER_PROFILES_URL, DEXSCREENER_TOKEN_URL, DEXSCREENER_SEARCH_URL

class DexScreenerClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TokenRiskRadar/1.0"
            })
        return self.session

    async def fetch_latest_profiles(self) -> List[Dict[str, Any]]:
        """Fetch latest token profiles with social and media links."""
        try:
            session = await self.get_session()
            async with session.get(DEXSCREENER_PROFILES_URL, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except Exception as e:
            print(f"[DexScreener] Error fetching latest profiles: {e}")
            return []

    async def fetch_token_pairs(self, token_address: str) -> List[Dict[str, Any]]:
        """Fetch all liquidity pairs for a token from DexScreener."""
        try:
            session = await self.get_session()
            url = DEXSCREENER_TOKEN_URL.format(address=token_address)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pairs", []) or []
                return []
        except Exception as e:
            print(f"[DexScreener] Error fetching token pairs for {token_address}: {e}")
            return []

    async def search_tokens(self, query: str) -> List[Dict[str, Any]]:
        """Search pairs by symbol, name, or address."""
        try:
            session = await self.get_session()
            url = DEXSCREENER_SEARCH_URL.format(query=query)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pairs", []) or []
                return []
        except Exception as e:
            print(f"[DexScreener] Error searching {query}: {e}")
            return []

    def extract_best_pair(self, pairs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the pair with highest liquidity."""
        if not pairs:
            return None
        # Sort by liquidity USD descending
        sorted_pairs = sorted(
            pairs,
            key=lambda p: float((p.get("liquidity", {}) or {}).get("usd", 0) or 0),
            reverse=True
        )
        return sorted_pairs[0]

    def parse_market_metrics(self, pair: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize market metrics from a DexScreener pair."""
        now_ms = time.time() * 1000
        created_at = pair.get("pairCreatedAt")
        
        age_hours = 0.0
        age_display = "Unknown"
        if created_at:
            elapsed_sec = max(0, (now_ms - created_at) / 1000)
            age_hours = round(elapsed_sec / 3600, 2)
            if age_hours < 1:
                age_display = f"{int(elapsed_sec // 60)} mins ago"
            elif age_hours < 24:
                age_display = f"{int(age_hours)} hours ago"
            else:
                age_display = f"{int(age_hours // 24)} days ago"

        liquidity = pair.get("liquidity", {}) or {}
        liq_usd = float(liquidity.get("usd", 0) or 0)
        fdv = float(pair.get("fdv", 0) or 0)
        mcap = float(pair.get("marketCap", 0) or fdv)
        price_usd = float(pair.get("priceUsd", 0) or 0)
        
        txns = pair.get("txns", {}) or {}
        txns_m5 = txns.get("m5", {}) or {}
        txns_h1 = txns.get("h1", {}) or {}
        txns_h24 = txns.get("h24", {}) or {}
        
        buys_h1 = int(txns_h1.get("buys", 0) or 0)
        sells_h1 = int(txns_h1.get("sells", 0) or 0)
        total_txns_h1 = buys_h1 + sells_h1
        
        volume = pair.get("volume", {}) or {}
        vol_m5 = float(volume.get("m5", 0) or 0)
        vol_h1 = float(volume.get("h1", 0) or 0)
        vol_h24 = float(volume.get("h24", 0) or 0)
        
        price_change = pair.get("priceChange", {}) or {}
        pc_m5 = float(price_change.get("m5", 0) or 0)
        pc_h1 = float(price_change.get("h1", 0) or 0)
        pc_h24 = float(price_change.get("h24", 0) or 0)
        
        info = pair.get("info", {}) or {}
        websites = info.get("websites", []) or []
        socials = info.get("socials", []) or []
        
        # Fake / Wash trading ratio estimation
        # If Volume is astronomically higher than liquidity in a tiny window with negligible price change
        wash_trading_score = 0
        if liq_usd > 0 and vol_h1 > 0:
            vol_to_liq = vol_h1 / liq_usd
            if vol_to_liq > 15 and abs(pc_h1) < 2.0:
                wash_trading_score = 75  # High probability of wash bots churning trades
            elif vol_to_liq > 8:
                wash_trading_score = 40

        return {
            "chain_id": pair.get("chainId", "unknown"),
            "dex_id": pair.get("dexId", "unknown"),
            "pair_address": pair.get("pairAddress", ""),
            "base_token_address": (pair.get("baseToken", {}) or {}).get("address", ""),
            "name": (pair.get("baseToken", {}) or {}).get("name", "Unknown Token"),
            "symbol": (pair.get("baseToken", {}) or {}).get("symbol", "UNKNOWN"),
            "price_usd": price_usd,
            "liquidity_usd": liq_usd,
            "fdv": fdv,
            "market_cap": mcap,
            "created_at_ms": created_at,
            "age_hours": age_hours,
            "age_display": age_display,
            "txns_h1": {
                "buys": buys_h1,
                "sells": sells_h1,
                "total": total_txns_h1,
                "buy_ratio": round((buys_h1 / total_txns_h1 * 100), 1) if total_txns_h1 > 0 else 50.0
            },
            "volume": {
                "m5": vol_m5,
                "h1": vol_h1,
                "h24": vol_h24
            },
            "price_change": {
                "m5": pc_m5,
                "h1": pc_h1,
                "h24": pc_h24
            },
            "socials": {
                "websites": websites,
                "socials": socials,
                "has_website": len(websites) > 0,
                "has_socials": len(socials) > 0,
                "image_url": info.get("imageUrl", "")
            },
            "wash_trading_risk": wash_trading_score,
            "dex_url": pair.get("url", "")
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
