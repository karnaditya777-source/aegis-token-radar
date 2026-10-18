"""
Educational case studies and benchmark profiles for demonstration and comparison.
Demonstrates various scam vectors (honeypot, hidden mint, dev dump, safe gem).
"""

from typing import Dict, Any, List

DEMO_CASE_STUDIES: List[Dict[str, Any]] = [
    {
        "id": "case_safe_gem",
        "title": "Solid Community Launch (Low Risk)",
        "chain": "solana",
        "market_data": {
            "chain_id": "solana",
            "dex_id": "raydium",
            "pair_address": "8sLb...RaydiumPool",
            "base_token_address": "SAFE111111111111111111111111111111111111111",
            "name": "Aegis Community Token",
            "symbol": "AEGIS",
            "price_usd": 0.042,
            "liquidity_usd": 240_000,
            "fdv": 4_200_000,
            "market_cap": 4_200_000,
            "age_hours": 36.5,
            "age_display": "1.5 days ago",
            "txns_h1": {
                "buys": 142,
                "sells": 98,
                "total": 240,
                "buy_ratio": 59.2
            },
            "volume": {
                "m5": 4200,
                "h1": 68000,
                "h24": 920000
            },
            "price_change": {
                "m5": 1.2,
                "h1": 5.4,
                "h24": 28.5
            },
            "socials": {
                "websites": [{"label": "Website", "url": "https://aegiscrypto.io"}],
                "socials": [{"type": "twitter", "url": "https://x.com/aegis_token"}, {"type": "telegram", "url": "https://t.me/aegis_portal"}],
                "has_website": True,
                "has_socials": True,
                "image_url": "https://cdn-icons-png.flaticon.com/512/9525/9525852.png"
            },
            "wash_trading_risk": 5,
            "dex_url": "https://dexscreener.com/solana/safe1"
        },
        "security_data": {
            "source": "audit_engine",
            "is_honeypot": False,
            "is_open_source": True,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "has_mint_authority": False,
            "has_freeze_authority": False,
            "is_mintable": False,
            "is_blacklisted": False,
            "can_take_back_ownership": False,
            "owner_change_balance": False,
            "selfdestruct": False,
            "hidden_owner": False,
            "is_renounced": True,
            "lp_locked_percent": 100.0,
            "top_10_percent": 18.5,
            "creator_percent": 0.0,
            "dev_total_percent": 0.0,
            "graph_insiders_count": 0,
            "is_metadata_mutable": False
        }
    },
    {
        "id": "case_honeypot",
        "title": "Classic Honeypot Scam (Cannot Sell)",
        "chain": "bsc",
        "market_data": {
            "chain_id": "bsc",
            "dex_id": "pancakeswap_v2",
            "pair_address": "0xTrap...Pool",
            "base_token_address": "0xHoneyPotFakeMoonToken1111111111111111111",
            "name": "Super Elon Rocket",
            "symbol": "ELONROCKET",
            "price_usd": 0.000085,
            "liquidity_usd": 12_500,
            "fdv": 850_000,
            "market_cap": 850_000,
            "age_hours": 1.2,
            "age_display": "1 hour ago",
            "txns_h1": {
                "buys": 118,
                "sells": 0,
                "total": 118,
                "buy_ratio": 100.0
            },
            "volume": {
                "m5": 1200,
                "h1": 25000,
                "h24": 25000
            },
            "price_change": {
                "m5": 8.0,
                "h1": 140.0,
                "h24": 140.0
            },
            "socials": {
                "websites": [],
                "socials": [],
                "has_website": False,
                "has_socials": False,
                "image_url": "https://cdn-icons-png.flaticon.com/512/3208/3208752.png"
            },
            "wash_trading_risk": 85,
            "dex_url": "https://dexscreener.com/bsc/honeypot"
        },
        "security_data": {
            "source": "audit_engine",
            "is_honeypot": True,
            "is_open_source": False,
            "buy_tax": 2.0,
            "sell_tax": 99.0,
            "is_mintable": True,
            "is_blacklisted": True,
            "can_take_back_ownership": True,
            "owner_change_balance": True,
            "selfdestruct": False,
            "hidden_owner": True,
            "is_renounced": False,
            "lp_locked_percent": 0.0,
            "top_10_percent": 94.2,
            "creator_percent": 42.0,
            "dev_total_percent": 42.0,
            "graph_insiders_count": 8,
            "is_metadata_mutable": True
        }
    },
    {
        "id": "case_unlocked_rug",
        "title": "Unlocked LP & Dev Concentration (High Risk)",
        "chain": "ethereum",
        "market_data": {
            "chain_id": "ethereum",
            "dex_id": "uniswap_v2",
            "pair_address": "0xUnsafe...Pool",
            "base_token_address": "0xUnlockedRugPullCandidate2222222222222222",
            "name": "Pepe Quantum AI",
            "symbol": "PEPEAI",
            "price_usd": 0.0034,
            "liquidity_usd": 8_200,
            "fdv": 340_000,
            "market_cap": 340_000,
            "age_hours": 0.4,
            "age_display": "24 mins ago",
            "txns_h1": {
                "buys": 32,
                "sells": 5,
                "total": 37,
                "buy_ratio": 86.5
            },
            "volume": {
                "m5": 2100,
                "h1": 15000,
                "h24": 15000
            },
            "price_change": {
                "m5": 22.0,
                "h1": 65.0,
                "h24": 65.0
            },
            "socials": {
                "websites": [{"label": "Website", "url": "https://pepeai-fake.surge.sh"}],
                "socials": [],
                "has_website": True,
                "has_socials": False,
                "image_url": "https://cdn-icons-png.flaticon.com/512/2619/2619275.png"
            },
            "wash_trading_risk": 35,
            "dex_url": "https://dexscreener.com/ethereum/pepeai"
        },
        "security_data": {
            "source": "audit_engine",
            "is_honeypot": False,
            "is_open_source": True,
            "buy_tax": 4.0,
            "sell_tax": 8.0,
            "is_mintable": True,
            "is_blacklisted": False,
            "can_take_back_ownership": False,
            "owner_change_balance": False,
            "selfdestruct": False,
            "hidden_owner": False,
            "is_renounced": False,
            "lp_locked_percent": 0.0,
            "top_10_percent": 78.4,
            "creator_percent": 28.5,
            "dev_total_percent": 28.5,
            "graph_insiders_count": 3,
            "is_metadata_mutable": True
        }
    },
    {
        "id": "case_speculative_meme",
        "title": "Viral Meme Launch (Speculative / Degen)",
        "chain": "solana",
        "market_data": {
            "chain_id": "solana",
            "dex_id": "raydium",
            "pair_address": "9kLm...Raydium",
            "base_token_address": "MEME333333333333333333333333333333333333333",
            "name": "Cat In Trenchcoat",
            "symbol": "COATCAT",
            "price_usd": 0.0089,
            "liquidity_usd": 65_000,
            "fdv": 890_000,
            "market_cap": 890_000,
            "age_hours": 4.5,
            "age_display": "4.5 hours ago",
            "txns_h1": {
                "buys": 210,
                "sells": 140,
                "total": 350,
                "buy_ratio": 60.0
            },
            "volume": {
                "m5": 8400,
                "h1": 120000,
                "h24": 450000
            },
            "price_change": {
                "m5": -3.2,
                "h1": 18.0,
                "h24": 88.0
            },
            "socials": {
                "websites": [{"label": "Website", "url": "https://catintrenchcoat.xyz"}],
                "socials": [{"type": "twitter", "url": "https://x.com/coatcat_sol"}],
                "has_website": True,
                "has_socials": True,
                "image_url": "https://cdn-icons-png.flaticon.com/512/616/616408.png"
            },
            "wash_trading_risk": 15,
            "dex_url": "https://dexscreener.com/solana/coatcat"
        },
        "security_data": {
            "source": "audit_engine",
            "is_honeypot": False,
            "is_open_source": True,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "has_mint_authority": False,
            "has_freeze_authority": False,
            "is_mintable": False,
            "is_blacklisted": False,
            "can_take_back_ownership": False,
            "owner_change_balance": False,
            "selfdestruct": False,
            "hidden_owner": False,
            "is_renounced": True,
            "lp_locked_percent": 100.0,
            "top_10_percent": 42.0,
            "creator_percent": 4.5,
            "dev_total_percent": 4.5,
            "graph_insiders_count": 1,
            "is_metadata_mutable": True
        }
    }
]
