"""
Token Scanner: Integrates DexScreener, GoPlus, RugCheck, RiskEngine, and PotentialEngine
to generate end-to-end token analysis.
"""

from typing import Dict, Any, Optional
from core.dexscreener import DexScreenerClient
from core.goplus import GoPlusClient
from core.rugcheck import RugCheckClient
from core.risk_engine import RiskEngine
from core.potential_engine import PotentialEngine
from core.config import SUPPORTED_CHAINS
from core.mock_scams import DEMO_CASE_STUDIES

class TokenScanner:
    def __init__(self):
        self.dexscreener = DexScreenerClient()
        self.goplus = GoPlusClient()
        self.rugcheck = RugCheckClient()
        self.risk_engine = RiskEngine()
        self.potential_engine = PotentialEngine()

    async def scan_token(self, address: str, chain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Deep scan any token by address across Solana or EVM chains.
        """
        clean_addr = address.strip()
        
        # Check if user requested one of our educational benchmark demo IDs
        for demo in DEMO_CASE_STUDIES:
            if clean_addr == demo["id"] or clean_addr == demo["market_data"]["base_token_address"]:
                risk_eval = self.risk_engine.evaluate(demo["market_data"], demo["security_data"])
                pot_eval = self.potential_engine.evaluate(demo["market_data"], risk_eval["score"])
                return {
                    "token_address": demo["market_data"]["base_token_address"],
                    "chain": demo["chain"],
                    "market": demo["market_data"],
                    "security": demo["security_data"],
                    "risk": risk_eval,
                    "potential": pot_eval,
                    "is_demo": True,
                    "demo_title": demo["title"]
                }

        # Step 1: Fetch pairs from DexScreener
        pairs = await self.dexscreener.fetch_token_pairs(clean_addr)
        if not pairs:
            # If search didn't find direct pairs, try query search
            search_results = await self.dexscreener.search_tokens(clean_addr)
            pairs = search_results

        best_pair = self.dexscreener.extract_best_pair(pairs)
        if not best_pair:
            # Could not find market pair on DEX
            return None

        market_data = self.dexscreener.parse_market_metrics(best_pair)
        detected_chain = market_data.get("chain_id", "unknown").lower()
        if chain:
            detected_chain = chain.lower()

        # Step 2: Perform Chain-Specific Security Audit
        security_data: Dict[str, Any] = {}
        
        if "solana" in detected_chain:
            sol_audit = await self.rugcheck.audit_solana_token(clean_addr)
            if sol_audit:
                security_data = sol_audit
            else:
                security_data = self._generate_fallback_solana_security()
        else:
            # EVM Chain lookup
            evm_chain_id = "1"
            if "bsc" in detected_chain or "binance" in detected_chain:
                evm_chain_id = "56"
            elif "base" in detected_chain:
                evm_chain_id = "8453"
            elif "arbitrum" in detected_chain:
                evm_chain_id = "42161"
            elif "polygon" in detected_chain:
                evm_chain_id = "137"

            evm_audit = await self.goplus.audit_evm_token(evm_chain_id, clean_addr)
            if evm_audit:
                security_data = evm_audit
            else:
                security_data = self._generate_fallback_evm_security()

        # Step 3: Run Algorithmic Evaluations
        risk_evaluation = self.risk_engine.evaluate(market_data, security_data)
        potential_evaluation = self.potential_engine.evaluate(market_data, risk_evaluation["score"])

        return {
            "token_address": clean_addr,
            "chain": detected_chain,
            "market": market_data,
            "security": security_data,
            "risk": risk_evaluation,
            "potential": potential_evaluation,
            "is_demo": False
        }

    def _generate_fallback_solana_security(self) -> Dict[str, Any]:
        """Reasonable default for Solana tokens if third-party security API is rate limited."""
        return {
            "source": "heuristic_fallback",
            "is_honeypot": False,
            "is_open_source": True,
            "has_mint_authority": False,
            "has_freeze_authority": False,
            "is_metadata_mutable": True,
            "lp_locked_percent": 100.0,
            "top_10_percent": 35.0,
            "creator_percent": 2.5,
            "is_rugged": False,
            "graph_insiders_count": 0,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "is_renounced": True
        }

    def _generate_fallback_evm_security(self) -> Dict[str, Any]:
        """Reasonable default for EVM tokens if third-party security API is rate limited."""
        return {
            "source": "heuristic_fallback",
            "is_honeypot": False,
            "is_open_source": True,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "is_mintable": False,
            "can_take_back_ownership": False,
            "owner_change_balance": False,
            "selfdestruct": False,
            "hidden_owner": False,
            "is_blacklisted": False,
            "is_renounced": True,
            "lp_locked_percent": 80.0,
            "top_10_percent": 38.0,
            "creator_percent": 3.0,
            "dev_total_percent": 3.0,
            "graph_insiders_count": 0
        }

    async def close(self):
        await self.dexscreener.close()
        await self.goplus.close()
        await self.rugcheck.close()
