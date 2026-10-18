"""
Configuration settings for Crypto Risk Detector & Rug Pull Analyzer
"""

SUPPORTED_CHAINS = {
    "solana": {
        "name": "Solana",
        "id": "solana",
        "symbol": "SOL",
        "explorer": "https://solscan.io/token/",
        "dex_id": ["raydium", "orca", "meteora", "pumpfun"]
    },
    "ethereum": {
        "name": "Ethereum",
        "id": "1",
        "symbol": "ETH",
        "explorer": "https://etherscan.io/token/",
        "dex_id": ["uniswap_v2", "uniswap_v3", "sushiswap"]
    },
    "base": {
        "name": "Base",
        "id": "8453",
        "symbol": "ETH",
        "explorer": "https://basescan.org/token/",
        "dex_id": ["aerodrome", "uniswap_v3"]
    },
    "bsc": {
        "name": "BNB Chain",
        "id": "56",
        "symbol": "BNB",
        "explorer": "https://bscscan.com/token/",
        "dex_id": ["pancakeswap_v2", "pancakeswap_v3"]
    },
    "arbitrum": {
        "name": "Arbitrum",
        "id": "42161",
        "symbol": "ETH",
        "explorer": "https://arbiscan.io/token/",
        "dex_id": ["camelot", "uniswap_v3"]
    }
}

# API endpoints
DEXSCREENER_PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"
DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens/{address}"
DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q={query}"
GECKOTERMINAL_NEW_POOLS_URL = "https://api.geckoterminal.com/api/v2/networks/new_pools?page=1"

GOPLUS_EVM_URL = "https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={address}"
GOPLUS_SOLANA_URL = "https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses={address}"
RUGCHECK_REPORT_URL = "https://api.rugcheck.xyz/v1/tokens/{address}/report"
RUGCHECK_SUMMARY_URL = "https://api.rugcheck.xyz/v1/tokens/{address}/report/summary"

# Cache TTLs (seconds)
CACHE_TTL_LATEST_TOKENS = 15
CACHE_TTL_TOKEN_ANALYSIS = 30
