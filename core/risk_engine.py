"""
Risk Engine: Algorithmic 0-100 Token Safety & Scam Assessment.
Evaluates smart contract security, liquidity locks, holder concentration,
honeypot behavior, owner privileges, and generates plain-English verdicts.
"""

from typing import Dict, Any, List, Tuple

class RiskEngine:
    def __init__(self):
        pass

    def evaluate(self, market_data: Dict[str, Any], security_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Risk Score (0-100) where:
        100 = Lowest Risk / Highest Security
        0 = Highest Risk / Definite Scam
        Generates Green Flags (✓), Warnings (⚠), and Red Flags (✗).
        """
        score = 100
        green_flags: List[str] = []
        warnings: List[str] = []
        red_flags: List[str] = []
        
        # 1. HONEYPOT & SELL RESTRICTIONS (FATAL)
        is_honeypot = security_data.get("is_honeypot", False)
        sell_tax = float(security_data.get("sell_tax") or 0.0)
        buy_tax = float(security_data.get("buy_tax") or 0.0)
        
        if is_honeypot:
            score -= 75
            red_flags.append("✗ Honeypot detected: Selling is restricted or blocked")
        elif sell_tax > 25.0:
            score -= 50
            red_flags.append(f"✗ Predatory sell tax ({sell_tax}%): Effectively a soft honeypot")
        elif sell_tax > 10.0:
            score -= 20
            warnings.append(f"⚠ High sell tax ({sell_tax}%) exceeds normal standards (<5%)")
        else:
            green_flags.append(f"✓ Normal buy/sell activity (Taxes: Buy {buy_tax}%, Sell {sell_tax}%)")

        # 2. SMART CONTRACT VERIFICATION & PERMISSIONS
        is_open_source = security_data.get("is_open_source", True)
        if not is_open_source:
            score -= 35
            red_flags.append("✗ Smart contract is NOT verified or open-source on block explorer")
        else:
            green_flags.append("✓ Contract verified and open-source")

        # Mint authority
        is_mintable = security_data.get("is_mintable", False) or security_data.get("has_mint_authority", False)
        if is_mintable:
            score -= 30
            red_flags.append("✗ Creator can mint unlimited additional tokens and dump")
        else:
            green_flags.append("✓ Mint authority disabled / non-mintable supply")

        # Freeze authority (Solana specific or EVM blacklist)
        has_freeze = security_data.get("has_freeze_authority", False)
        is_blacklisted = security_data.get("is_blacklisted", False)
        if has_freeze:
            score -= 35
            red_flags.append("✗ Freeze authority enabled: Creator can freeze any wallet's tokens")
        elif is_blacklisted:
            score -= 20
            red_flags.append("✗ Blacklist function detected: Owner can arbitrarily block addresses")
        else:
            green_flags.append("✓ No wallet freezing or blacklist permissions detected")

        # Dangerous owner functions (EVM)
        can_take_back_ownership = security_data.get("can_take_back_ownership", False)
        owner_change_balance = security_data.get("owner_change_balance", False)
        selfdestruct = security_data.get("selfdestruct", False)
        hidden_owner = security_data.get("hidden_owner", False)

        if can_take_back_ownership:
            score -= 30
            red_flags.append("✗ Owner can reclaim contract ownership at any time")
        if owner_change_balance:
            score -= 40
            red_flags.append("✗ Dangerous permission: Owner can modify token balances directly")
        if selfdestruct:
            score -= 25
            red_flags.append("✗ Selfdestruct opcode present in contract bytecode")
        if hidden_owner:
            score -= 25
            red_flags.append("✗ Hidden owner detected behind proxy / secondary controller")

        # Renounced ownership
        is_renounced = security_data.get("is_renounced", False)
        if is_renounced:
            green_flags.append("✓ Contract ownership renounced / burned")
        else:
            warnings.append("⚠ Contract ownership is active (not renounced)")

        # 3. LIQUIDITY & LOCK STATUS
        liq_usd = float(market_data.get("liquidity_usd", 0) or 0)
        lp_locked_pct = float(security_data.get("lp_locked_percent", 0) or 0)

        # Check LP Lock
        if lp_locked_pct >= 85.0:
            green_flags.append(f"✓ Liquidity securely locked or burned ({lp_locked_pct}%)")
        elif lp_locked_pct >= 50.0:
            score -= 12
            warnings.append(f"⚠ Partial liquidity lock ({lp_locked_pct}% locked, remainder unlocked)")
        elif lp_locked_pct > 0.0:
            score -= 25
            warnings.append(f"⚠ Low liquidity lock ({lp_locked_pct}% locked): Creator holds majority LP")
        else:
            score -= 35
            red_flags.append("✗ Liquidity is NOT locked (0% locked/burned): High rug pull danger")

        # Check Liquidity Depth
        if liq_usd >= 100_000:
            green_flags.append(f"✓ Deep liquidity pool (${liq_usd:,.0f})")
        elif liq_usd >= 20_000:
            green_flags.append(f"✓ Adequate initial liquidity (${liq_usd:,.0f})")
        elif liq_usd >= 5_000:
            score -= 10
            warnings.append(f"⚠ Low liquidity (${liq_usd:,.0f}): High slippage for trades")
        else:
            score -= 25
            red_flags.append(f"✗ Extremely fragile liquidity (${liq_usd:,.0f}): High risk of pool drainage")

        # 4. HOLDER CONCENTRATION & DEV HOLDINGS
        top_10_pct = float(security_data.get("top_10_percent", 0) or 0)
        dev_pct = float(security_data.get("creator_percent", 0) or security_data.get("dev_total_percent", 0) or 0)

        if top_10_pct > 75.0:
            score -= 30
            red_flags.append(f"✗ Extreme concentration: Top 10 holders own {top_10_pct}% of total supply")
        elif top_10_pct > 40.0:
            score -= 15
            warnings.append(f"⚠ High concentration: Top 10 holders own {top_10_pct}% of supply")
        elif top_10_pct > 0:
            green_flags.append(f"✓ Healthy holder distribution (Top 10 hold {top_10_pct}%)")

        if dev_pct > 20.0:
            score -= 30
            red_flags.append(f"✗ Developer / Deployer wallet holds {dev_pct}% of supply (Massive dump risk)")
        elif dev_pct > 8.0:
            score -= 12
            warnings.append(f"⚠ Developer holds significant allocation ({dev_pct}%)")
        elif dev_pct > 0:
            green_flags.append(f"✓ Low developer wallet holding ({dev_pct}%)")

        # Insider networks check
        graph_insiders = int(security_data.get("graph_insiders_count", 0) or 0)
        if graph_insiders > 0:
            score -= 18
            warnings.append(f"⚠ Insider wallet clusters detected ({graph_insiders} linked wallets)")

        # 5. TOKEN AGE & TIME RISKS
        age_hours = float(market_data.get("age_hours", 0) or 0)
        if age_hours < 0.5:
            score -= 15
            warnings.append(f"⚠ Token is ultra new ({market_data.get('age_display', 'minutes ago')}): Extreme volatility window")
        elif age_hours < 6.0:
            score -= 8
            warnings.append(f"⚠ Token launched recently ({market_data.get('age_display', 'hours ago')})")
        else:
            green_flags.append(f"✓ Survived initial launch window (Age: {market_data.get('age_display', 'hours old')})")

        # 6. TRADING PATTERNS & VOLUME MANIPULATION
        wash_risk = int(market_data.get("wash_trading_risk", 0) or 0)
        if wash_risk >= 50:
            score -= 20
            red_flags.append("✗ Suspicious volume patterns: High probability of wash trading / fake bots")
        
        txns_h1 = market_data.get("txns_h1", {}) or {}
        buys = txns_h1.get("buys", 0)
        sells = txns_h1.get("sells", 0)
        if buys > 20 and sells == 0:
            score -= 30
            red_flags.append(f"✗ Zero sells recorded ({buys} buys, 0 sells): Strong indicator of honeypot")

        # 7. SOCIAL PRESENCE & METADATA
        socials = market_data.get("socials", {}) or {}
        has_website = socials.get("has_website", False)
        has_socials = socials.get("has_socials", False)
        is_metadata_mutable = security_data.get("is_metadata_mutable", False)

        if has_website or has_socials:
            green_flags.append("✓ Project website and social links provided")
        else:
            score -= 8
            warnings.append("⚠ No verified website or social links attached (Ghost launch)")

        if is_metadata_mutable:
            warnings.append("⚠ Token metadata is mutable (Name/Symbol/Logo can be altered by creator)")

        # Clamp score between 0 and 100
        score = max(0, min(100, score))

        # Risk level categorization
        if score >= 75:
            risk_level = "Relatively Low Risk"
            risk_badge = "🟢"
            risk_category = "safe"
            verdict = "Contract appears legitimate with healthy liquidity safeguards and standard trading parameters."
        elif score >= 50:
            risk_level = "Moderate / Speculative Risk"
            risk_badge = "🟡"
            risk_category = "speculative"
            verdict = "Some cautionary factors identified (e.g. young age, partial locks, or active ownership). Trade with tight stop losses."
        elif score >= 25:
            risk_level = "High Risk"
            risk_badge = "🟠"
            risk_category = "high_risk"
            verdict = "Significant red flags detected such as unlocked liquidity, concentrated holdings, or dangerous permissions."
        else:
            risk_level = "Extremely High Risk / Probable Scam"
            risk_badge = "🔴"
            risk_category = "extreme_risk"
            verdict = "Severe scam or honeypot mechanics identified. Capital loss is virtually guaranteed."

        return {
            "score": score,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "risk_category": risk_category,
            "verdict": verdict,
            "green_flags": green_flags,
            "warnings": warnings,
            "red_flags": red_flags,
            "pillars": {
                "contract_security": self._calculate_pillar_score([
                    (not is_honeypot, 30),
                    (is_open_source, 25),
                    (not is_mintable, 20),
                    (not has_freeze and not is_blacklisted, 15),
                    (sell_tax <= 10.0, 10)
                ]),
                "liquidity_health": self._calculate_pillar_score([
                    (lp_locked_pct >= 80.0, 50),
                    (liq_usd >= 20_000, 30),
                    (liq_usd >= 5_000, 20)
                ]),
                "holder_distribution": self._calculate_pillar_score([
                    (top_10_pct <= 40.0, 45),
                    (dev_pct <= 8.0, 35),
                    (graph_insiders == 0, 20)
                ]),
                "trading_integrity": self._calculate_pillar_score([
                    (wash_risk < 40, 40),
                    (not (buys > 15 and sells == 0), 40),
                    (age_hours >= 6.0, 20)
                ])
            }
        }

    def _calculate_pillar_score(self, checks: List[Tuple[bool, int]]) -> int:
        total = sum(weight for condition, weight in checks if condition)
        return min(100, max(0, total))
