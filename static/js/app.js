/**
 * Crypto Token Risk & Rug Pull Radar - Frontend Logic
 */

let activeChain = 'all';
let activeCategory = 'all';
let activeMinLiquidity = 0;
let searchQuery = '';
let isAutoRefresh = true;
let isAudioEnabled = false;
let autoRefreshTimer = null;
let currentActiveToken = null;

// Audio Chime Generator using Web Audio API
function playSafeTokenAlert() {
  if (!isAudioEnabled) return;
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880.00, audioCtx.currentTime + 0.15); // A5
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.35);
  } catch (e) {
    console.warn("Audio chime error:", e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initUIEventListeners();
  fetchStats();
  fetchTokens();
  startAutoRefresh();
});

function initUIEventListeners() {
  // Chain filters
  document.querySelectorAll('[data-chain]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('[data-chain]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeChain = btn.getAttribute('data-chain');
      fetchTokens();
    });
  });

  // Risk filters
  document.querySelectorAll('[data-category]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('[data-category]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-category');
      fetchTokens();
    });
  });

  // Liquidity filter
  const liqSelect = document.getElementById('selectLiquidity');
  if (liqSelect) {
    liqSelect.addEventListener('change', (e) => {
      activeMinLiquidity = parseFloat(e.target.value) || 0;
      fetchTokens();
    });
  }

  // Search input
  const searchInput = document.getElementById('inputSearch');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        searchQuery = e.target.value.trim();
        fetchTokens();
      }, 300);
    });
  }

  // On-demand Contract Scanner
  const btnScan = document.getElementById('btnScan');
  const inputScan = document.getElementById('inputScanAddress');
  if (btnScan && inputScan) {
    btnScan.addEventListener('click', () => {
      const addr = inputScan.value.trim();
      if (addr) scanTokenAddress(addr);
    });
    inputScan.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const addr = inputScan.value.trim();
        if (addr) scanTokenAddress(addr);
      }
    });
  }

  // Refresh button
  const btnRefresh = document.getElementById('btnRefresh');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      fetchStats();
      fetchTokens();
    });
  }

  // Sound toggle button
  const btnSound = document.getElementById('btnSound');
  if (btnSound) {
    btnSound.addEventListener('click', () => {
      isAudioEnabled = !isAudioEnabled;
      btnSound.innerHTML = isAudioEnabled ? '🔔 Alert Chime: ON' : '🔕 Alert Chime: OFF';
      btnSound.style.borderColor = isAudioEnabled ? 'var(--safe-green)' : 'var(--border-color)';
    });
  }

  // Modal close
  const modalClose = document.getElementById('modalClose');
  const modalOverlay = document.getElementById('modalOverlay');
  if (modalClose && modalOverlay) {
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }

  // Demo pills
  document.querySelectorAll('[data-demo-id]').forEach(pill => {
    pill.addEventListener('click', () => {
      const demoId = pill.getAttribute('data-demo-id');
      scanTokenAddress(demoId);
    });
  });

  // Export report button
  const btnExport = document.getElementById('btnExportReport');
  if (btnExport) {
    btnExport.addEventListener('click', exportTokenReport);
  }

  // Cookie Consent & Preference Handlers
  initCookieConsent();
}

// Cookie Helper Functions
function setCookie(name, value, days) {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + encodeURIComponent(value || "") + expires + "; path=/; SameSite=Lax";
}

function getCookie(name) {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
  }
  return null;
}

function deleteCookie(name) {
  document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function initCookieConsent() {
  const banner = document.getElementById('cookieBanner');
  const modal = document.getElementById('cookieModalOverlay');
  const consent = getCookie('aegis_cookie_consent');

  // If user hasn't chosen cookie consent yet, show banner
  if (!consent && banner) {
    setTimeout(() => {
      banner.classList.add('active');
    }, 800);
  }

  // Restore saved preferences from cookies
  const savedChain = getCookie('aegis_pref_chain');
  if (savedChain && document.querySelector(`[data-chain="${savedChain}"]`)) {
    document.querySelectorAll('[data-chain]').forEach(b => b.classList.remove('active'));
    const targetBtn = document.querySelector(`[data-chain="${savedChain}"]`);
    if (targetBtn) {
      targetBtn.classList.add('active');
      activeChain = savedChain;
    }
  }

  const savedSound = getCookie('aegis_pref_sound');
  if (savedSound === 'true') {
    isAudioEnabled = true;
    const btnSound = document.getElementById('btnSound');
    if (btnSound) {
      btnSound.innerHTML = '🔔 Alert Chime: ON';
      btnSound.style.borderColor = 'var(--safe-green)';
    }
  }

  // Accept All button
  const btnAccept = document.getElementById('btnAcceptCookies');
  if (btnAccept && banner) {
    btnAccept.addEventListener('click', () => {
      setCookie('aegis_cookie_consent', 'accepted', 365);
      setCookie('aegis_pref_chain', activeChain, 180);
      setCookie('aegis_pref_sound', isAudioEnabled, 180);
      banner.classList.remove('active');
    });
  }

  // Essential Only button
  const btnEssential = document.getElementById('btnEssentialCookies');
  if (btnEssential && banner) {
    btnEssential.addEventListener('click', () => {
      setCookie('aegis_cookie_consent', 'essential', 365);
      deleteCookie('aegis_pref_chain');
      deleteCookie('aegis_pref_sound');
      banner.classList.remove('active');
    });
  }

  // Preferences Modal Trigger
  const btnManage = document.getElementById('btnManageCookies');
  const modalClose = document.getElementById('cookieModalClose');
  if (btnManage && modal) {
    btnManage.addEventListener('click', () => {
      modal.classList.add('active');
    });
  }
  if (modalClose && modal) {
    modalClose.addEventListener('click', () => {
      modal.classList.remove('active');
    });
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }

  // Save Preferences in Modal
  const btnSave = document.getElementById('btnSaveCookiePrefs');
  const checkPref = document.getElementById('checkPrefCookies');
  if (btnSave && modal) {
    btnSave.addEventListener('click', () => {
      setCookie('aegis_cookie_consent', 'customized', 365);
      if (checkPref && checkPref.checked) {
        setCookie('aegis_pref_chain', activeChain, 180);
        setCookie('aegis_pref_sound', isAudioEnabled, 180);
      } else {
        deleteCookie('aegis_pref_chain');
        deleteCookie('aegis_pref_sound');
      }
      modal.classList.remove('active');
      if (banner) banner.classList.remove('active');
    });
  }

  // Clear Cookies button
  const btnClear = document.getElementById('btnClearCookies');
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      deleteCookie('aegis_cookie_consent');
      deleteCookie('aegis_pref_chain');
      deleteCookie('aegis_pref_sound');
      alert('All Aegis cookies have been cleared.');
      if (modal) modal.classList.remove('active');
      if (banner) banner.classList.add('active');
    });
  }
}

function startAutoRefresh() {
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(() => {
    if (isAutoRefresh) {
      fetchStats();
      fetchTokens(true);
    }
  }, 10000); // 10 seconds
}

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    const stats = data.stats || {};

    const elTotal = document.getElementById('statTotalDetected');
    const elScams = document.getElementById('statScamsCaught');
    const elSafe = document.getElementById('statSafeGems');

    if (elTotal) elTotal.innerText = stats.total_detected || '0';
    if (elScams) elScams.innerText = stats.scams_caught || '0';
    if (elSafe) elSafe.innerText = stats.safe_gems_found || '0';
  } catch (e) {
    console.error("Error fetching stats:", e);
  }
}

async function fetchTokens(isBackground = false) {
  const container = document.getElementById('tokensGrid');
  if (!isBackground && container) {
    // Show spinner only on manual or initial fetch
    // (don't flicker UI during background polling)
    if (container.children.length === 0) {
      container.innerHTML = `
        <div class="loading-box" style="grid-column: 1 / -1;">
          <div class="spinner"></div>
          <p>Listening to live DEX pool creations...</p>
        </div>
      `;
    }
  }

  try {
    const params = new URLSearchParams();
    if (activeChain !== 'all') params.append('chain', activeChain);
    if (activeCategory !== 'all') params.append('risk_category', activeCategory);
    if (activeMinLiquidity > 0) params.append('min_liquidity', activeMinLiquidity);
    if (searchQuery) params.append('q', searchQuery);

    const res = await fetch(`/api/tokens/latest?${params.toString()}`);
    if (!res.ok) throw new Error("API error");
    const data = await res.json();
    const tokens = data.tokens || [];

    renderTokensGrid(tokens);
  } catch (e) {
    console.error("Error fetching tokens:", e);
    if (container && container.children.length === 0) {
      container.innerHTML = `
        <div class="loading-box" style="grid-column: 1 / -1;">
          <p style="color: var(--extreme-risk-red);">Failed to connect to scanner API.</p>
        </div>
      `;
    }
  }
}

function renderTokensGrid(tokens) {
  const container = document.getElementById('tokensGrid');
  if (!container) return;

  if (tokens.length === 0) {
    container.innerHTML = `
      <div class="loading-box" style="grid-column: 1 / -1;">
        <p>No tokens matched your filter criteria. Try selecting "All Chains" or lowering min liquidity.</p>
      </div>
    `;
    return;
  }

  let html = '';
  tokens.forEach((t, idx) => {
    const m = t.market || {};
    const r = t.risk || {};
    const p = t.potential || {};
    const s = t.security || {};

    const score = r.score ?? 50;
    const cat = r.risk_category || 'speculative';
    const badge = r.risk_badge || '🟡';
    const level = r.risk_level || 'Moderate Risk';

    const symbol = m.symbol || 'UNKNOWN';
    const name = m.name || 'Unnamed Token';
    const chain = t.chain || 'solana';
    const age = m.age_display || 'Recent';

    const liq = m.liquidity_usd ? `$${formatCompactNumber(m.liquidity_usd)}` : '$0';
    const lpLocked = s.lp_locked_percent !== undefined ? `${s.lp_locked_percent}%` : 'Unk';
    const vol1h = m.volume?.h1 ? `$${formatCompactNumber(m.volume.h1)}` : '$0';
    const pc1h = m.price_change?.h1 ? `${m.price_change.h1 > 0 ? '+' : ''}${m.price_change.h1}%` : '0%';

    // Top 3 key flags for card preview
    const keyFlags = [];
    if (r.red_flags && r.red_flags.length > 0) {
      keyFlags.push({ type: 'red', text: r.red_flags[0] });
    }
    if (r.warnings && r.warnings.length > 0 && keyFlags.length < 3) {
      keyFlags.push({ type: 'warn', text: r.warnings[0] });
    }
    if (r.green_flags && r.green_flags.length > 0 && keyFlags.length < 3) {
      keyFlags.push({ type: 'green', text: r.green_flags[0] });
    }
    if (r.green_flags && r.green_flags.length > 1 && keyFlags.length < 3) {
      keyFlags.push({ type: 'green', text: r.green_flags[1] });
    }

    const avatar = m.socials?.image_url 
      ? `<img src="${m.socials.image_url}" class="token-avatar" onerror="this.src=''; this.innerText='${symbol.slice(0, 2)}';">`
      : `<div class="token-avatar">${symbol.slice(0, 2)}</div>`;

    html += `
      <div class="token-card" onclick="openTokenAuditModal('${t.token_address}')">
        <div class="token-card-header">
          <div class="token-identity">
            ${avatar}
            <div class="token-name-wrap">
              <h3>${escapeHtml(symbol)}</h3>
              <div class="token-sub">
                <span class="chain-badge ${chain.toLowerCase()}">${chain}</span>
                <span>• ${age}</span>
              </div>
            </div>
          </div>
          <div class="score-badge-wrap">
            <div class="risk-score-pill ${cat}">
              <span>${score}</span><small>/100</small> <span>${badge}</span>
            </div>
            <div class="risk-level-caption ${cat}">${level}</div>
          </div>
        </div>

        <div class="market-strip">
          <div class="strip-item">
            <span class="strip-label">LIQUIDITY</span>
            <span class="strip-val">${liq}</span>
          </div>
          <div class="strip-item">
            <span class="strip-label">LP LOCKED</span>
            <span class="strip-val" style="color: ${s.lp_locked_percent >= 80 ? 'var(--safe-green)' : (s.lp_locked_percent > 0 ? 'var(--warning-yellow)' : 'var(--extreme-risk-red)')};">
              ${lpLocked}
            </span>
          </div>
          <div class="strip-item">
            <span class="strip-label">1H VOL / CHG</span>
            <span class="strip-val">${vol1h} <span style="font-size: 0.72rem; color: ${m.price_change?.h1 >= 0 ? '#34d399' : '#f87171'};">(${pc1h})</span></span>
          </div>
        </div>

        <ul class="flags-preview-list">
          ${keyFlags.map(f => `<li class="${f.type}">${escapeHtml(f.text)}</li>`).join('')}
        </ul>

        <div class="card-footer">
          <span class="quadrant-pill">${escapeHtml(p.quadrant || 'Analyzed')}</span>
          <button class="btn-inspect" onclick="event.stopPropagation(); openTokenAuditModal('${t.token_address}')">
            Deep Audit ➔
          </button>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

async function scanTokenAddress(address) {
  const btn = document.getElementById('btnScan');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; margin: 0; border-width: 2px;"></div> Scanning...';
  }

  try {
    const res = await fetch(`/api/tokens/scan?address=${encodeURIComponent(address)}`);
    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Failed to scan token. Ensure contract address has an active DEX pair.");
      return;
    }
    const tokenData = await res.json();
    openModalWithData(tokenData);
  } catch (e) {
    console.error("Scan error:", e);
    alert("Error communicating with scanner engine.");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = 'Scan Contract';
    }
  }
}

async function openTokenAuditModal(address) {
  try {
    const res = await fetch(`/api/tokens/scan?address=${encodeURIComponent(address)}`);
    if (res.ok) {
      const data = await res.json();
      openModalWithData(data);
    }
  } catch (e) {
    console.error("Modal load error:", e);
  }
}

function openModalWithData(token) {
  currentActiveToken = token;
  const modal = document.getElementById('modalOverlay');
  if (!modal) return;

  const m = token.market || {};
  const r = token.risk || {};
  const p = token.potential || {};
  const s = token.security || {};

  // Title & Header
  document.getElementById('modalTokenSymbol').innerText = m.symbol || 'UNKNOWN';
  document.getElementById('modalTokenName').innerText = m.name || 'Unknown Token';
  document.getElementById('modalTokenChain').innerText = (token.chain || 'SOLANA').toUpperCase();
  document.getElementById('modalTokenAddress').innerText = token.token_address;

  // External Links
  const linkDex = document.getElementById('linkDexscreener');
  if (linkDex) linkDex.href = m.dex_url || `https://dexscreener.com/search?q=${token.token_address}`;

  const linkExp = document.getElementById('linkExplorer');
  if (linkExp) {
    const ch = (token.chain || '').toLowerCase();
    if (ch.includes('solana')) linkExp.href = `https://solscan.io/token/${token.token_address}`;
    else if (ch.includes('bsc')) linkExp.href = `https://bscscan.com/token/${token.token_address}`;
    else if (ch.includes('base')) linkExp.href = `https://basescan.org/token/${token.token_address}`;
    else linkExp.href = `https://etherscan.io/token/${token.token_address}`;
  }

  // Dual Score Banner
  const riskBox = document.getElementById('modalRiskBox');
  riskBox.className = `score-box risk-box ${r.risk_category || 'speculative'}`;
  
  document.getElementById('modalRiskScore').innerText = `${r.score ?? 50}/100`;
  document.getElementById('modalRiskScore').style.color = getCategoryColor(r.risk_category);
  document.getElementById('modalRiskBadge').innerText = r.risk_badge || '🟡';
  document.getElementById('modalRiskLevel').innerText = r.risk_level || 'Moderate';
  document.getElementById('modalRiskVerdict').innerText = r.verdict || '';

  // Potential Score
  document.getElementById('modalPotentialScore').innerText = `${p.score ?? 50}/100`;
  document.getElementById('modalPotentialBadge').innerText = p.badge || '📈';
  document.getElementById('modalPotentialLevel').innerText = p.level || 'Moderate';
  document.getElementById('modalQuadrantName').innerText = p.quadrant || 'Market Profile';
  document.getElementById('modalQuadrantDesc').innerText = p.quadrant_description || '';

  // Itemized Checklist
  const renderChecklist = (items, elementId) => {
    const ul = document.getElementById(elementId);
    if (!ul) return;
    if (!items || items.length === 0) {
      ul.innerHTML = '<li style="color: var(--text-dim); font-style: italic;">None detected</li>';
    } else {
      ul.innerHTML = items.map(it => `<li>${escapeHtml(it)}</li>`).join('');
    }
  };

  renderChecklist(r.green_flags, 'listGreenFlags');
  renderChecklist(r.warnings, 'listWarnings');
  renderChecklist(r.red_flags, 'listRedFlags');

  // Four Pillars Progress Bars
  const pillars = r.pillars || {};
  setProgressBar('barContractSec', 'valContractSec', pillars.contract_security || 50);
  setProgressBar('barLiquidity', 'valLiquidity', pillars.liquidity_health || 50);
  setProgressBar('barHolders', 'valHolders', pillars.holder_distribution || 50);
  setProgressBar('barTrading', 'valTrading', pillars.trading_integrity || 50);

  // Deep Details Table
  document.getElementById('tdAge').innerText = m.age_display || 'Unknown';
  document.getElementById('tdLiquidity').innerText = m.liquidity_usd ? `$${formatNumber(m.liquidity_usd)}` : '$0';
  document.getElementById('tdLpLock').innerText = `${s.lp_locked_percent ?? 0}% locked`;
  document.getElementById('tdMcap').innerText = m.market_cap ? `$${formatNumber(m.market_cap)}` : '$0';
  document.getElementById('tdTaxes').innerText = `Buy: ${s.buy_tax ?? 0}% | Sell: ${s.sell_tax ?? 0}%`;
  document.getElementById('tdTop10').innerText = `${s.top_10_percent ?? 0}% of total supply`;
  document.getElementById('tdDevHoldings').innerText = `${s.creator_percent ?? s.dev_total_percent ?? 0}%`;
  document.getElementById('tdHoneypot').innerText = s.is_honeypot ? 'FAIL (Honeypot Detected)' : 'PASS (Selling Allowed)';
  document.getElementById('tdHoneypot').style.color = s.is_honeypot ? 'var(--extreme-risk-red)' : 'var(--safe-green)';
  document.getElementById('tdMintable').innerText = (s.is_mintable || s.has_mint_authority) ? 'WARNING (Mintable Supply)' : 'SAFE (Non-mintable)';
  document.getElementById('tdFreezable').innerText = (s.has_freeze_authority || s.is_blacklisted) ? 'DANGER (Freezable / Blacklist)' : 'SAFE (No Freezing)';
  document.getElementById('tdRenounced').innerText = s.is_renounced ? 'YES (Renounced / Null Owner)' : 'NO (Owner Active)';

  // Show modal
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function setProgressBar(barId, valId, value) {
  const bar = document.getElementById(barId);
  const val = document.getElementById(valId);
  if (bar) {
    bar.style.width = `${value}%`;
    bar.style.backgroundColor = value >= 75 ? 'var(--safe-green)' : (value >= 50 ? 'var(--warning-yellow)' : 'var(--extreme-risk-red)');
  }
  if (val) val.innerText = `${value}%`;
}

function closeModal() {
  const modal = document.getElementById('modalOverlay');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = 'auto';
  currentActiveToken = null;
}

function exportTokenReport() {
  if (!currentActiveToken) return;
  const t = currentActiveToken;
  const m = t.market || {};
  const r = t.risk || {};
  const s = t.security || {};
  const p = t.potential || {};

  const report = `# TOKEN RISK AUDIT REPORT
**Token**: ${m.name} (${m.symbol})
**Address**: \`${t.token_address}\`
**Chain**: ${t.chain}
**Generated**: ${new Date().toISOString()}

---

## 🛡️ RISK SCORE: ${r.score}/100 ${r.risk_badge} (${r.risk_level})
**Verdict**: ${r.verdict}

### Itemized Security Checklist:
${(r.green_flags || []).map(f => `- ${f}`).join('\n')}
${(r.warnings || []).map(w => `- ${w}`).join('\n')}
${(r.red_flags || []).map(rf => `- ${rf}`).join('\n')}

---

## 🚀 MARKET POTENTIAL: ${p.score}/100 ${p.badge} (${p.level})
**Classification**: ${p.quadrant}
**Details**: ${p.quadrant_description}

### Market Metrics:
- **Liquidity**: $${formatNumber(m.liquidity_usd || 0)}
- **LP Locked**: ${s.lp_locked_percent || 0}%
- **Market Cap**: $${formatNumber(m.market_cap || 0)}
- **Taxes**: Buy ${s.buy_tax || 0}% / Sell ${s.sell_tax || 0}%
- **Top 10 Holders**: ${s.top_10_percent || 0}%
- **Dev Holding**: ${s.creator_percent || 0}%
- **Age**: ${m.age_display || 'Unknown'}

---
*Disclaimer: Generated by Crypto Token Risk Radar. This assessment reflects code security heuristics and does not constitute financial advice.*
`;

  // Download report file
  const blob = new Blob([report], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${m.symbol || 'token'}_risk_report.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// Helpers
function formatNumber(num) {
  return Number(num).toLocaleString('en-US', { maximumFractionDigits: 2 });
}

function formatCompactNumber(num) {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(1) + 'K';
  return Number(num).toFixed(2);
}

function getCategoryColor(cat) {
  switch (cat) {
    case 'safe': return 'var(--safe-green)';
    case 'speculative': return 'var(--warning-yellow)';
    case 'high_risk': return 'var(--high-risk-orange)';
    case 'extreme_risk': return 'var(--extreme-risk-red)';
    default: return 'var(--text-main)';
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
