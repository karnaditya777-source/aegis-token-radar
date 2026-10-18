"""
Startup script for Crypto Token Risk & Rug Pull Radar.
"""

import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    print("\n[AEGIS RADAR] Opening browser at http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 65)
    print("  🛡️  AEGIS CRYPTO TOKEN RISK & RUG PULL RADAR ")
    print("  Live Multi-Chain Scanner: Solana, Base, Ethereum, BSC")
    print("=" * 65)
    
    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Uvicorn server
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info")
