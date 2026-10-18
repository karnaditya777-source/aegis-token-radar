"""
GoPlus Security API integration for EVM & Solana smart contract security audits.
"""

import aiohttp
from typing import Dict, Any, Optional, List
from core.config import GOPLUS_EVM_URL, GOPLUS_SOLANA_URL

KNOWN_BURN_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
    "11111111111111111111111111111111", # Solana system program / burn
}

KNOWN_LOCKERS = [
    "unicrypt", "pinksale", "team finance", "mudra", "dxsale", 
    "deep lock", "floki fi", "raydium authority"
]

class GoPlusClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TokenRiskRadar/1.0"
            })
        return self.session

    async def audit_evm_token(self, chain_id: str, address: str) -> Optional[Dict[str, Any]]:
        """Audit an EVM token using GoPlus Security API."""
        try:
            session = await self.get_session()
            url = GOPLUS_EVM_URL.format(chain_id=chain_id, address=address)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get("result", {})
                    token_data = result.get(address.lower())
                    if token_data:
                        return self._parse_evm_security(token_data)
                return None
        except Exception as e:
            print(f"[GoPlus] EVM audit error for {address} on chain {chain_id}: {e}")
            return None

    def _parse_evm_security(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw GoPlus EVM security response into structured security metrics."""
        is_honeypot = raw.get("is_honeypot") == "1" or raw.get("cannot_sell_all") == "1"
        is_open_source = raw.get("is_open_source") == "1"
        
        buy_tax = float(raw.get("buy_tax") or 0.0) * 100.0
        sell_tax = float(raw.get("sell_tax") or 0.0) * 100.0
        
        is_mintable = raw.get("is_mintable") == "1"
        can_take_back_ownership = raw.get("can_take_back_ownership") == "1"
        owner_change_balance = raw.get("owner_change_balance") == "1"
        hidden_owner = raw.get("hidden_owner") == "1"
        selfdestruct = raw.get("selfdestruct") == "1"
        is_blacklisted = raw.get("is_blacklisted") == "1"
        is_whitelisted = raw.get("is_whitelisted") == "1"
        anti_whale_modifiable = raw.get("anti_whale_modifiable") == "1"
        slippage_modifiable = raw.get("slippage_modifiable") == "1"
        trading_cooldown = raw.get("trading_cooldown") == "1"
        transfer_pausable = raw.get("transfer_pausable") == "1"

        owner_address = raw.get("owner_address", "")
        creator_address = raw.get("creator_address", "")
        
        # Check ownership status
        is_renounced = (
            not owner_address or 
            owner_address.lower() in KNOWN_BURN_ADDRESSES or 
            owner_address == "0x"
        )
        
        creator_percent = float(raw.get("creator_percent") or 0.0) * 100.0
        owner_percent = float(raw.get("owner_percent") or 0.0) * 100.0
        dev_total_percent = round(creator_percent + owner_percent, 2)
        
        # Calculate LP Locked Percentage
        lp_holders = raw.get("lp_holders", []) or []
        lp_locked_percent = 0.0
        lp_lock_details = []
        for lph in lp_holders:
            holder_addr = (lph.get("address") or "").lower()
            tag = (lph.get("tag") or "").lower()
            is_locked = lph.get("is_locked") == 1
            pct = float(lph.get("percent") or 0.0) * 100.0
            
            is_burn = holder_addr in KNOWN_BURN_ADDRESSES or "null" in tag or "burn" in tag or "dead" in tag
            is_known_locker = any(locker in tag for locker in KNOWN_LOCKERS)
            
            if is_locked or is_burn or is_known_locker:
                lp_locked_percent += pct
                lp_lock_details.append({
                    "address": holder_addr,
                    "tag": lph.get("tag") or ("Burn Address" if is_burn else "Locker"),
                    "percent": round(pct, 2),
                    "end_time": lph.get("end_time")
                })
        
        lp_locked_percent = min(100.0, round(lp_locked_percent, 2))

        # Top 10 token holders concentration (excluding known burn addresses and LP contracts)
        holders = raw.get("holders", []) or []
        top_10_percent = 0.0
        top_holders_list = []
        for idx, h in enumerate(holders[:10]):
            h_addr = (h.get("address") or "").lower()
            pct = float(h.get("percent") or 0.0) * 100.0
            is_contract = h.get("is_contract") == 1
            is_locked = h.get("is_locked") == 1
            
            # Don't penalize dead addresses or verified locked contracts
            if h_addr not in KNOWN_BURN_ADDRESSES:
                top_10_percent += pct
            
            top_holders_list.append({
                "address": h_addr,
                "percent": round(pct, 2),
                "is_contract": is_contract,
                "is_locked": is_locked,
                "tag": h.get("tag", "")
            })
        
        top_10_percent = min(100.0, round(top_10_percent, 2))

        return {
            "source": "goplus_evm",
            "is_honeypot": is_honeypot,
            "is_open_source": is_open_source,
            "buy_tax": round(buy_tax, 2),
            "sell_tax": round(sell_tax, 2),
            "is_mintable": is_mintable,
            "can_take_back_ownership": can_take_back_ownership,
            "owner_change_balance": owner_change_balance,
            "hidden_owner": hidden_owner,
            "selfdestruct": selfdestruct,
            "is_blacklisted": is_blacklisted,
            "is_whitelisted": is_whitelisted,
            "anti_whale_modifiable": anti_whale_modifiable,
            "slippage_modifiable": slippage_modifiable,
            "trading_cooldown": trading_cooldown,
            "transfer_pausable": transfer_pausable,
            "is_renounced": is_renounced,
            "owner_address": owner_address,
            "creator_address": creator_address,
            "creator_percent": round(creator_percent, 2),
            "dev_total_percent": dev_total_percent,
            "lp_locked_percent": lp_locked_percent,
            "lp_lock_details": lp_lock_details,
            "top_10_percent": top_10_percent,
            "top_holders": top_holders_list,
            "holder_count": int(raw.get("holder_count") or 0)
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
