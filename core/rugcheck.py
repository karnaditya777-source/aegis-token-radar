"""
RugCheck API client for Solana token security, mint/freeze authorities, and insider graph checks.
"""

import aiohttp
from typing import Dict, Any, Optional, List
from core.config import RUGCHECK_REPORT_URL, RUGCHECK_SUMMARY_URL

class RugCheckClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TokenRiskRadar/1.0",
                "Accept": "application/json"
            })
        return self.session

    async def audit_solana_token(self, mint_address: str) -> Optional[Dict[str, Any]]:
        """Fetch deep audit report from RugCheck.xyz."""
        try:
            session = await self.get_session()
            url = RUGCHECK_REPORT_URL.format(address=mint_address)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_solana_report(data)
                
                # Fallback to summary if full report is unavailable
                summary_url = RUGCHECK_SUMMARY_URL.format(address=mint_address)
                async with session.get(summary_url, timeout=aiohttp.ClientTimeout(total=6)) as s_resp:
                    if s_resp.status == 200:
                        s_data = await s_resp.json()
                        return self._parse_solana_summary(s_data, mint_address)
                return None
        except Exception as e:
            print(f"[RugCheck] Solana audit error for {mint_address}: {e}")
            return None

    def _parse_solana_report(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RugCheck full report into unified security format."""
        token_info = raw.get("token", {}) or {}
        token_meta = raw.get("tokenMeta", {}) or {}
        
        mint_authority = raw.get("mintAuthority") or token_info.get("mintAuthority")
        freeze_authority = raw.get("freezeAuthority") or token_info.get("freezeAuthority")
        
        has_mint_authority = mint_authority is not None and str(mint_authority).strip() != ""
        has_freeze_authority = freeze_authority is not None and str(freeze_authority).strip() != ""
        
        # Metadata mutability
        is_metadata_mutable = token_meta.get("mutable", True)
        
        # LP Locked percentage
        lp_locked_pct = float(raw.get("lpLockedPct") or 0.0)
        markets = raw.get("markets", []) or []
        if isinstance(markets, list):
            for m in markets:
                lp_info = m.get("lp", {}) or {}
                market_lp_locked = float(lp_info.get("lpLockedPct") or 0.0)
                if market_lp_locked > lp_locked_pct:
                    lp_locked_pct = market_lp_locked

        lockers = raw.get("lockers")
        if isinstance(lockers, dict) and len(lockers) > 0 and lp_locked_pct == 0.0:
            for lock_id, lock_val in lockers.items():
                if isinstance(lock_val, dict) and float(lock_val.get("usdcLocked") or 0) > 1000:
                    lp_locked_pct = 99.0
                    break

        # Known DEX / AMM Pool Owners on Solana (do not count DEX pool as whale dump wallet)
        KNOWN_SOL_POOLS = {
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", # Raydium AMM v4
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK", # Raydium CLMM
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",  # Orca Whirlpool
            "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",  # Meteora DLMM
            "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",  # OpenBook
            "11111111111111111111111111111111"               # Burn
        }

        # Top holders
        top_holders_raw = raw.get("topHolders", []) or []
        top_10_percent = 0.0
        top_holders_list = []
        for idx, h in enumerate(top_holders_raw[:15]):
            pct = float(h.get("pct") or 0.0)
            addr = h.get("address", "")
            owner = h.get("owner", "")
            is_insider = h.get("insider", False)
            is_pool = owner in KNOWN_SOL_POOLS or addr in KNOWN_SOL_POOLS

            if not is_pool and len(top_holders_list) < 10:
                top_10_percent += pct
                top_holders_list.append({
                    "address": addr,
                    "percent": round(pct, 2),
                    "insider": is_insider,
                    "owner": owner,
                    "is_pool": is_pool
                })
        top_10_percent = min(100.0, round(top_10_percent, 2))

        # Dev / Creator balance
        creator_balance = float(raw.get("creatorBalance") or 0.0)
        creator_addr = raw.get("creator", "")

        # Rugged flag & insider networks
        is_rugged = raw.get("rugged", False)
        graph_insiders = raw.get("graphInsidersDetected", 0) or 0
        insider_networks = raw.get("insiderNetworks", []) or []
        
        risks = raw.get("risks", []) or []
        risk_descriptions = [r.get("description", r.get("name", "")) for r in risks if r]

        # Is honeypot simulation
        # In Solana, having freeze authority enabled is an active honeypot risk
        is_honeypot = has_freeze_authority or is_rugged

        return {
            "source": "rugcheck_solana",
            "is_honeypot": is_honeypot,
            "is_open_source": True,  # Solana standard token program
            "has_mint_authority": has_mint_authority,
            "mint_authority": mint_authority,
            "has_freeze_authority": has_freeze_authority,
            "freeze_authority": freeze_authority,
            "is_metadata_mutable": is_metadata_mutable,
            "lp_locked_percent": round(lp_locked_pct, 2),
            "top_10_percent": top_10_percent,
            "top_holders": top_holders_list,
            "creator_address": creator_addr,
            "creator_percent": 0.0,  # Sol balance parsed if available
            "is_rugged": is_rugged,
            "graph_insiders_count": graph_insiders,
            "risks": risk_descriptions,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "is_renounced": (not has_mint_authority and not has_freeze_authority)
        }

    def _parse_solana_summary(self, raw: Dict[str, Any], mint_address: str) -> Dict[str, Any]:
        risks = raw.get("risks", []) or []
        risk_descs = [r.get("name", "") for r in risks]
        has_freeze = any("freeze" in d.lower() for d in risk_descs)
        has_mint = any("mint" in d.lower() for d in risk_descs)
        lp_locked = float(raw.get("lpLockedPct") or 0.0)

        return {
            "source": "rugcheck_summary",
            "is_honeypot": has_freeze,
            "is_open_source": True,
            "has_mint_authority": has_mint,
            "mint_authority": "Active" if has_mint else None,
            "has_freeze_authority": has_freeze,
            "freeze_authority": "Active" if has_freeze else None,
            "is_metadata_mutable": True,
            "lp_locked_percent": round(lp_locked, 2),
            "top_10_percent": 0.0,
            "top_holders": [],
            "creator_address": "",
            "creator_percent": 0.0,
            "is_rugged": False,
            "graph_insiders_count": 0,
            "risks": risk_descs,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "is_renounced": (not has_mint and not has_freeze)
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
