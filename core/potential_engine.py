"""
Potential & Market Momentum Engine.
Distinguishes between "Security Risk" and "Market Upside Potential".
A token can be 100% safe (renounced contract, locked LP) yet have 0 buyers (dead token),
or conversely possess viral hype while being technically precarious.
"""

from typing import Dict, Any, List

class PotentialEngine:
    def __init__(self):
        pass

    def evaluate(self, market_data: Dict[str, Any], risk_score: int) -> Dict[str, Any]:
        """
        Calculates Potential Score (0-100) based on market traction,
        liquidity depth, volume acceleration, and buyer demand.
        """
        score = 0
        factors: List[str] = []

        liq_usd = float(market_data.get("liquidity_usd", 0) or 0)
        mcap = float(market_data.get("market_cap", 0) or market_data.get("fdv", 0) or 0)
        vol_h1 = float(market_data.get("volume", {}).get("h1", 0) or 0)
        vol_m5 = float(market_data.get("volume", {}).get("m5", 0) or 0)
        pc_h1 = float(market_data.get("price_change", {}).get("h1", 0) or 0)
        
        txns_h1 = market_data.get("txns_h1", {}) or {}
        buys_h1 = int(txns_h1.get("buys", 0) or 0)
        sells_h1 = int(txns_h1.get("sells", 0) or 0)
        total_txns = buys_h1 + sells_h1
        buy_ratio = float(txns_h1.get("buy_ratio", 50.0))

        # 1. Volume & Velocity (up to 30 pts)
        if vol_h1 >= 250_000:
            score += 30
            factors.append(f"Explosive trading volume (${vol_h1:,.0f} in past hour)")
        elif vol_h1 >= 50_000:
            score += 22
            factors.append(f"Strong 1h trading volume (${vol_h1:,.0f})")
        elif vol_h1 >= 10_000:
            score += 15
            factors.append(f"Healthy early volume (${vol_h1:,.0f})")
        elif vol_h1 >= 2_000:
            score += 8
            factors.append("Moderate trading activity")
        else:
            factors.append("Low volume: Lack of immediate market liquidity")

        # 2. Buyer Demand & Accumulation (up to 25 pts)
        if total_txns >= 200 and buy_ratio >= 65.0:
            score += 25
            factors.append(f"High buyer accumulation ({buy_ratio}% buys across {total_txns} trades)")
        elif total_txns >= 50 and buy_ratio >= 55.0:
            score += 18
            factors.append(f"Positive buy pressure ({buy_ratio}% buys)")
        elif total_txns >= 20:
            score += 10
            factors.append("Balanced buy/sell participation")
        else:
            score += 2
            factors.append("Low transaction count: Community has not yet discovered the pair")

        # 3. Liquidity-to-Market-Cap Backing (up to 20 pts)
        if mcap > 0 and liq_usd > 0:
            liq_to_mcap = liq_usd / mcap
            if 0.15 <= liq_to_mcap <= 0.6:
                score += 20
                factors.append("Ideal liquidity-to-market-cap ratio (Sustainable backing)")
            elif liq_to_mcap > 0.6:
                score += 12
                factors.append("High liquidity ratio: Lower price volatility")
            elif liq_to_mcap < 0.05:
                score += 5
                factors.append("Thin liquidity relative to market cap (High slippage & pump/dump risk)")

        # 4. Social & Virality Presence (up to 15 pts)
        socials = market_data.get("socials", {}) or {}
        has_web = socials.get("has_website", False)
        has_soc = socials.get("has_socials", False)
        if has_web and has_soc:
            score += 15
            factors.append("Full social presence (Website + Active community channels)")
        elif has_web or has_soc:
            score += 8
            factors.append("Partial project links present")
        else:
            factors.append("No official social links detected")

        # 5. Price Momentum (up to 10 pts)
        if 5.0 <= pc_h1 <= 150.0:
            score += 10
            factors.append(f"Upward price momentum (+{pc_h1}% in 1h)")
        elif pc_h1 > 150.0:
            score += 6
            factors.append(f"Parabolic run (+{pc_h1}%): High risk of mean reversion")
        elif pc_h1 < -30.0:
            score += 0
            factors.append(f"Heavy sell-off ({pc_h1}% in 1h)")

        score = max(0, min(100, score))

        # Categorize potential
        if score >= 75:
            potential_level = "High Growth Momentum"
            potential_badge = "🚀"
        elif score >= 50:
            potential_level = "Moderate Potential"
            potential_badge = "📈"
        elif score >= 25:
            potential_level = "Developing / Low Activity"
            potential_badge = "⏳"
        else:
            potential_level = "Stagnant / Dead Pair"
            potential_badge = "💤"

        # Determine Quadrant Matrix
        # Risk Score: 70+ is Low Risk (Safe), <50 is High Risk
        # Potential Score: 50+ is High Potential, <50 is Low Potential
        if risk_score >= 65 and score >= 50:
            quadrant = "Safe Accumulator"
            quadrant_description = "High contract security combined with active market demand. Ideal profile for lower-risk crypto exposure."
        elif risk_score >= 65 and score < 50:
            quadrant = "Safe but Inactive"
            quadrant_description = "The contract is technically secure and safe from scams, but currently lacks trading volume or community hype."
        elif risk_score < 45 and score >= 50:
            quadrant = "High-Risk Hype / Degen Gamble"
            quadrant_description = "Strong volume and price movement, but severe smart contract risks or unlock dangers. High chance of sudden developer dump."
        else:
            quadrant = "Toxic / Low-Value"
            quadrant_description = "Both high security risk and dead market traction. Best avoided."

        return {
            "score": score,
            "level": potential_level,
            "badge": potential_badge,
            "quadrant": quadrant,
            "quadrant_description": quadrant_description,
            "momentum_factors": factors,
            "distinction_note": (
                "REMINDER: A high safety score guarantees the token cannot easily rug or entrap your funds; "
                "it does not guarantee profit. Market potential measures community demand and trading volume."
            )
        }
