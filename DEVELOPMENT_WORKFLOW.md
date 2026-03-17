# Development Workflow - Git Branch Strategy

## 🌳 Branch Structure

```
main (production-ready)
└── dev (development branch)
    ├── feature/new-feature
    ├── feature/bug-fix
    └── feature/enhancement
```

## 📋 Workflow Rules

### **Main Branch (`main`)**
- ✅ **Production-ready code only**
- ✅ **No direct commits** - only merges from dev
- ✅ **Always stable and tested**
- ✅ **Tagged releases**

### **Development Branch (`dev`)**
- ✅ **Active development**
- ✅ **Feature integration**
- ✅ **Testing ground**
- ✅ **Regular commits allowed**

### **Feature Branches (`feature/*`)**
- ✅ **One feature per branch**
- ✅ **Branch from dev**
- ✅ **Merge back to dev when complete**
- ✅ **Delete after merge**

---

## 🚀 Development Workflow

### **1. Start New Feature**
```bash
# Switch to dev branch
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature...
```

### **2. Commit Changes**
```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: add new feature description"

# Push feature branch
git push -u origin feature/your-feature-name
```

### **3. Merge Feature to Dev**
```bash
# Switch to dev
git checkout dev
git pull origin dev

# Merge feature branch
git merge feature/your-feature-name

# Push dev
git push origin dev

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### **4. Release to Main (When Ready)**
```bash
# Switch to main
git checkout main
git pull origin main

# Merge dev to main
git merge dev

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"

# Push main and tags
git push origin main --tags
```

---

## 📝 Commit Message Convention

Use conventional commits:

```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance tasks
```

---

## 🔄 Daily Workflow

### **Morning: Start Work**
```bash
git checkout dev
git pull origin dev
git checkout -b feature/daily-task
```

### **Throughout Day: Regular Commits**
```bash
git add .
git commit -m "feat: implement X functionality"
git push
```

### **Evening: Merge to Dev**
```bash
git checkout dev
git merge feature/daily-task
git push origin dev
```

---

## 🛠️ Useful Commands

### **Check Status**
```bash
git status                    # Current status
git branch -a                 # All branches
git log --oneline -5          # Recent commits
```

### **Switch Branches**
```bash
git checkout main             # Switch to main
git checkout dev              # Switch to dev
git checkout -b feature/new   # Create and switch to feature
```

### **Sync with Remote**
```bash
git pull origin dev           # Pull latest dev
git push origin dev           # Push dev changes
```

### **Clean Up**
```bash
git branch -d feature/old     # Delete local branch
git push origin --delete feature/old  # Delete remote branch
```

---

## ⚠️ Important Rules

1. **Never commit directly to main**
2. **Always pull before pushing**
3. **Test before merging to main**
4. **Delete feature branches after merge**
5. **Use clear commit messages**

---

## 🎯 Branch Status

| Branch | Commit | Notes |
|--------|--------|-------|
| `main` | `e6d90a5` | Last production baseline |
| `dev`  | `f0eddca` | Current integration branch |
| `TA-STRAT-001` | `338439c` | Strategy layer + dashboard status split + backtest alignment (open PR branch) |

> ⚠️ **Note (March 11):** PR #5 (`feature/dashboard-live-refresh`) was merged into `main` instead of `dev` on GitHub. Fixed by fast-forwarding `dev` to `origin/main`. Both branches are now aligned. Future PRs should target `dev`.

---

## 📊 Project Status — Updated March 17, 2026

### What Was Completed Recently

| Area | Yesterday | Today | Status |
|------|-----------|-------|--------|
| **Web Dashboard** | Live status existed but market/scanner semantics were mixed | Split status into real market session + scanner active window | ✅ Resolved |
| **Strategy Layer** | Decision logic mixed inside paper execution | Explicit `src/strategies.py` with deterministic contract and tests | ✅ Resolved |
| **Paper Trading Flow** | Strategy and execution tightly coupled | Strategy evaluates, paper engine executes signals | ✅ Resolved |
| **Backtesting** | Placeholder tag rules | Uses shared strategy signals for entry/exit decisions | ✅ Improved |
| **Cloud Deployment** | Docker only, no cloud target | No change | 🔲 Still partial |
| **Automated Trading** | No broker integration | No change | 🔲 Missing |
| **Monitoring / Logging** | File logging only | No change | 🔲 Basic |

### What Was Committed Today (March 17)

```
338439c  refactor: align backtest with strategy layer signals
b9dc748  feat: add explicit strategy layer and scanner/market status split
```

### Previous Milestone (March 11)

```
e6d90a5  Merge PR #5 feature/dashboard-live-refresh → main
17fcaf8  feat: add live JS polling to dashboard (15s auto-refresh)
b83f636  fix: correct committed_capital key typo in /api/summary endpoint
de813bf  fix: continue to Yahoo fallback when Polygon/Alpha are rate-limited
78d786c  Merge PR #4 feature/db-migrations
7a621fa  chore: initialize flask-migrate with baseline schema
8ef8924  Merge PR #3 feature/improve-email-alerts
0ddf57e  feat: consolidate trading alerts into one summary email
bdd3fc9  Merge PR #2 feature/paper-trading-engine
7a72404  feat: implement paper trading engine with RSI strategy and dashboard
```

### System Architecture — Current State

```
trading_agent.py (main loop)
  ├── strategies.py         ← explicit entry/exit decision layer
  ├── paper_trading.py      ← signal execution only
  ├── utils.py              ← data fetch (4-source fallback), indicators, email, market hours
  ├── alert_formatter.py    ← builds one consolidated email per cycle
  └── database.py           ← SQLAlchemy models, Flask app, Flask-Migrate

web/app.py (Flask routes)
  ├── GET /                 ← server-rendered dashboard (Jinja)
  ├── GET /api/summary      ← live summary JSON (market session + scanner status)
  ├── GET /api/paper-positions
  ├── GET /api/paper-trades
  ├── GET /api/data
  └── GET /api/health

web/templates/dashboard.html
  └── JS polling: /api/summary + /api/paper-positions + /api/paper-trades

migrations/
  └── 81e81464848c_baseline_existing_schema.py  ← empty baseline, DB stamped
```

### Strongest Parts Right Now

- ✅ Containerized (Docker + docker-compose)
- ✅ Signal generation with RSI, EMAs, ATR, volatility tags
- ✅ Consolidated email alerts (one per cycle)
- ✅ SQLite persistence with migration safety net
- ✅ Paper trading engine with stop/target, P&L tracking
- ✅ Live dashboard with auto-refresh (no page reload needed)
- ✅ Clear status semantics: market open vs scanner active window
- ✅ 4-level data fallback chain (resilient to API rate limits)
- ✅ Strategy-specific deterministic tests + manual suite passing

---

## 🚀 Recommended Next Steps (Priority Order)

### 1. `feature/monitoring-logs` — HIGH PRIORITY
Now that strategy decisions are explicit, observability is the biggest gap.
- Add `/api/metrics` endpoint exposing cycle count, last successful cycle time, and recent error count
- Add structured logging (JSON or key-value) for signal decisions and email delivery results
- Add scanner heartbeat to dashboard status bar (last cycle time + last email result)

### 2. `feature/backtest-reports` — MEDIUM PRIORITY
Backtest now uses strategy signals, but result handling is still basic.
- Persist backtest results to JSON or DB instead of console-only output
- Add baseline metrics: win rate, avg win/loss, max drawdown, trade count
- Add optional parameter sweeps for RSI and ATR multipliers

### 3. `feature/utils-split` — MEDIUM PRIORITY
`utils.py` still mixes several responsibilities.
- Split into `data_sources.py`, `indicators.py`, `alerts.py`, and `market_hours.py`
- Keep compatibility imports to reduce regression risk
- Add module-level tests for each split component

### 4. `feature/cloud-deployment` — LOWER PRIORITY (after strategy is solid)
The Docker image already exists. What's needed:
- `docker-compose.prod.yml` with env-var secrets (not hardcoded)
- Deploy target: Railway, Render, or Fly.io (simpler than ECS for this scale)
- Managed SQLite → PostgreSQL migration via Flask-Migrate

### 5. `feature/broker-integration` — FUTURE
Alpaca paper API is free and well-documented. Long-term target once strategy engine is validated.

---

## ⚠️ Known Technical Debt

| Item | File | Notes |
|------|------|-------|
| `utils.py` does too much | `src/utils.py` | Mixes data fetch, indicators, email, market hours, options |
| No structured logging | `src/trading_agent.py` | `print()` + basic file log only |
| SQLite not suitable for cloud | `src/database.py` | Fine for local/dev, needs swap before cloud deployment |
| No CSRF protection on Flask | `web/app.py` | Read-only API for now, but worth adding before any write endpoints |

---

*Last Updated: March 17, 2026*
