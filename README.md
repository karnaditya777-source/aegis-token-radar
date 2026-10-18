# 🛡️ Aegis Token Radar: Real-Time Crypto Scam & Risk Intelligence

An automated multi-chain cryptocurrency detection and security analysis platform that monitors newly launched tokens the moment they appear on decentralized exchanges (DEXs) and calculates an algorithmic **Risk Score from 0 to 100** alongside an objective **Market Potential Score**.

Built to evaluate whether a new token is legitimate, highly speculative, or a fatal scam/rug pull.

---

## 🌟 Key Features

### 1. Real-Time Token Launch Detection
- **Multi-Chain Radar**: Continuously monitors new liquidity pool creations across **Solana, Ethereum, Base, and BNB Chain (BSC)** using real-time decentralized exchange feeds.
- **Immediate Audit**: Every newly detected token is instantly audited for contract vulnerabilities, liquidity lock status, and whale concentration.

### 2. Algorithmic Risk Scoring (0–100) & Categorization
- **100 / 100** represents maximal contract security and safety.
- **0 / 100** represents critical scam mechanics (e.g. Honeypot, 99% sell tax, malicious minting).
- **Four Risk Categories**:
  - `75 – 100` 🟢 **Relatively Low Risk**: Verified source, ownership renounced/clean, locked liquidity, no malicious backdoors.
  - `50 – 74` 🟡 **Moderate / Speculative**: Young token, active ownership, or partial lock.
  - `25 – 49` 🟠 **High Risk**: Substantial red flags, high dev concentration, or unlocked LP.
  - `0 – 24` 🔴 **Extremely High Risk / Probable Scam**: Active honeypot, freezable wallets, hidden owner, or 0% lock.

### 3. Plain-English Security Checklist (User Specified Format)
Generates transparent, bulleted verdicts:
- **✓ Green Flags**: Confirmed safeguards (`✓ Contract verified`, `✓ Liquidity locked (100%)`, `✓ Mint authority disabled`, `✓ Healthy distribution`).
- **⚠ Warnings**: Cautionary factors (`⚠ Token is only 45 minutes old`, `⚠ Active unrenounced ownership`, `⚠ Mutable metadata`).
- **✗ Red Flags**: Fatal dangers (`✗ Honeypot detected: Selling is restricted`, `✗ Top 10 wallets hold 92% of supply`, `✗ Creator can freeze arbitrary wallets`).

### 4. Clear Separation Between "Risk" and "Potential"
- **Risk Score**: Evaluates whether the contract is safe from technical fraud, rug pulls, and entrapment.
- **Potential Score (0–100)**: Evaluates volume velocity, buyer accumulation (buy/sell ratio), liquidity backing, and community traction.
- **Classification Quadrant**:
  - `Safe Accumulator`: High safety + strong market traction.
  - `Safe but Inactive`: High safety, but 0 volume (safe contract, dead community).
  - `Degen Gamble`: Viral trading volume, but precarious unlock risks or dev holdings.
  - `Toxic / Low-Value`: Both insecure and dead.

### 5. Multi-Chain Deep Audit Coverage
| Category | Evaluated Parameters |
| :--- | :--- |
| **Token Age & Velocity** | Pair creation timestamp, hours elapsed, initial volatility window. |
| **Liquidity & Lock** | LP depth ($ USD), LP burned or locked %, lock provider (Unicrypt, PinkSale, Mudra, Raydium burn). |
| **Contract Security** | Verified open source, honeypot test, buy/sell taxes, hidden owner, selfdestruct opcode. |
| **Owner Permissions** | Mint authority (unlimited supply printing), Freeze authority (freezing accounts), Blacklist ability. |
| **Holder Distribution** | Top 10 holders %, deployer/creator wallet balance %, insider cluster networks. |
| **Trading Integrity** | Buy vs Sell transaction ratio, wash trading / fake volume bots detection. |
| **Project Socials** | Verified website, Twitter/X, Telegram presence, mutable vs immutable metadata. |

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `requests`, `aiohttp`

```bash
pip install fastapi uvicorn requests aiohttp
```

### 2. Launch the Application
Run the startup script:
```bash
python run.py
```
This automatically starts the server and opens your browser at **`http://localhost:8000`**.

Alternatively, run with Uvicorn:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Interactive cyber dark-mode web dashboard. |
| `/api/tokens/latest` | `GET` | Live feed of newly detected tokens with query filters (`chain`, `risk_category`, `min_liquidity`, `q`). |
| `/api/tokens/scan` | `GET` | Deep scan any token contract address or Solana mint (`?address=0x...&chain=...`). |
| `/api/stats` | `GET` | Live stats (total tokens scanned, scams caught, safe gems found, detector status). |
| `/api/demo/samples` | `GET` | Built-in educational benchmark cases (Safe Gem, Honeypot, Unlocked Rug, Degen Meme). |
| `/api/chains` | `GET` | List of supported blockchain networks with explorer configurations. |

---

## 🧪 Built-in Benchmark Demos

The dashboard includes one-click benchmark testing scenarios:
1. **🟢 Solid Community Token (`AEGIS`)**: 100% LP locked, contract renounced, 0% dev dump, healthy distribution. (Score: `100/100`)
2. **🔴 Classic Honeypot (`ELONROCKET`)**: Unverified bytecode, 99% sell tax, blacklist function, zero sells recorded. (Score: `0/100`)
3. **🔴 Unlocked LP Rug Pull (`PEPEAI`)**: 0% liquidity locked, creator owns 28% of supply, unrenounced owner. (Score: `28/100`)
4. **🟡 Viral Meme Token (`COATCAT`)**: 100% LP locked and clean contract, but 4.5 hours old and mutable metadata. (Score: `72/100`)

---

## 📑 Project Structure

```
antigravity/
├── app.py                 # FastAPI backend server with REST endpoints & static hosting
├── config.py              # Configuration & network endpoints
├── core/
│   ├── config.py          # Supported chains and API URLs
│   ├── detector.py        # Background DEX launch detector & real-time poller
│   ├── scanner.py         # Multi-chain orchestrator (EVM + Solana)
│   ├── dexscreener.py     # DexScreener market data, volume, age & socials
│   ├── goplus.py          # GoPlus Security client for EVM smart contract audits
│   ├── rugcheck.py        # RugCheck client for Solana token mint/freeze authorities
│   ├── risk_engine.py     # 0-100 Risk Scoring algorithm & plain-English bullet generator
│   ├── potential_engine.py# Market Momentum & Risk vs Potential matrix engine
│   └── mock_scams.py      # Benchmark profiles for instant comparison & education
├── static/
│   ├── css/style.css      # Dark-mode glassmorphic styling
│   ├── js/app.js          # Interactive frontend logic, polling, filters, modal inspector
│   └── index.html         # Web application dashboard
├── run.py                 # Startup script with auto-browser launch
└── README.md              # Documentation
```
