# Project Roadmap

This roadmap turns the current checklist into an execution plan for the existing trading agent codebase.

## Status Update - March 17, 2026

Completed in TA-STRAT-001 and recent prior milestones:

- Explicit strategy layer added (`src/strategies.py`) with deterministic signal contract.
- Live loop now evaluates strategy first and executes paper signals second.
- Paper trading flow is decoupled from strategy decision logic.
- Dashboard now distinguishes market session status from scanner-window status.
- Backtest now consumes strategy-layer signals rather than placeholder logic.
- Tests are reorganized in `tests/`, and `./cli.sh test` includes strategy-layer coverage.

Current biggest gaps after this milestone:

- Structured logging and runtime observability (`/api/metrics`, cycle/error visibility).
- Backtest result persistence and reporting (win rate, drawdown, parameter comparison).
- `src/utils.py` modular split to reduce coupling.
- Cloud hardening path (secrets + PostgreSQL + deployment shape).
- Broker integration remains intentionally deferred.

## Current State

The project already has these working foundations:

- Dockerized runtime for local deployment
- Email-based signal alerts
- SQLite persistence for market data, alerts, and options snapshots
- Flask dashboard for basic visibility
- Backtesting module using backtrader
- Technical indicators including EMA, ATR, IV proxy, and RSI
- Explicit strategy layer used by live and backtest flows
- Paper trading ledger with open/closed position lifecycle
- Flask-Migrate baseline and migration scaffolding

The project is still missing these key capabilities:

- Cloud deployment target for 24/7 uptime
- Structured monitoring and health metrics
- Backtest result reports and parameter analysis
- Modularized utility architecture
- Broker API integration for future automation

## Phase 1: Stabilize The Core

Goal: make the current app easier to maintain and safer to extend.

### 1.1 Reorganize tests

Move root-level ad hoc tests into the `tests/` package.

Target changes:

- Move `test_manual.py` into `tests/test_manual.py`
- Move `test_basic.py` into `tests/test_basic.py`
- Move `test_imports.py` into `tests/test_imports.py`
- Move `test_agent_run.py` into `tests/test_agent_run.py`
- Update `cli.sh` to run tests from the `tests/` directory

Why this matters:

- Keeps the project root clean
- Makes future automated testing easier
- Separates smoke checks from application code

### 1.2 Add database migrations

Introduce a migration tool so schema changes do not require deleting the database.

Recommended approach:

- Add Flask-Migrate or Alembic
- Generate migrations for existing tables
- Create migration for the `rsi` column in `MarketData`

Target changes:

- `requirements.txt`
- `src/database.py`
- new migration directory

Why this matters:

- Prevents runtime failures when models evolve
- Allows SQLite now and PostgreSQL later without manual schema resets

### 1.3 Split `src/utils.py`

The current utility module contains too many responsibilities.

Recommended split:

- `src/data_sources.py` for Polygon, Alpha Vantage, Yahoo, and options fetches
- `src/indicators.py` for EMA, ATR, volatility, RSI, and metric calculation
- `src/alerts.py` for email formatting and delivery
- `src/market_hours.py` for schedule logic

Why this matters:

- Makes strategy development easier
- Reduces regression risk when adding features
- Improves readability of the live loop

## Phase 2: Make Signals Actionable

Goal: turn alerting into a repeatable trading workflow.

### 2.1 Add a strategy layer

Introduce explicit trading rules on top of the current market tags.

Recommended first strategy:

- Long-only mean reversion on `SPY` and `QQQ`
- Entry when `OVERSOLD` and not `TRENDING_DOWN`
- Optional confirmation when price is above `EMA50`
- Exit on RSI recovery or ATR-based stop

Target changes:

- new `src/strategies.py`
- update `src/trading_agent.py`

Why this matters:

- Alerts become interpretable trade candidates
- Rules become testable and backtestable

### 2.2 Add a paper trading engine

Create a lightweight simulation layer that tracks fake orders and portfolio state.

Minimum scope:

- Starting cash balance
- Open positions
- Closed trades
- Entry and exit reasons
- P&L tracking

Suggested database objects:

- `PaperPosition`
- `PaperTrade`
- `PaperAccountSnapshot`

Target changes:

- new `src/paper_trading.py`
- `src/database.py`
- `src/trading_agent.py`

Why this matters:

- Lets you validate whether alerts produce profitable actions
- Bridges the gap between notifications and broker integration

### 2.3 Improve email content

Turn raw condition alerts into operator-friendly trade summaries.

Recommended additions:

- Current RSI value
- Strategy context
- Suggested action: watch / consider long / avoid / neutral
- Risk context using ATR

Target changes:

- `src/trading_agent.py`
- email formatting logic in the alerts module

## Phase 3: Upgrade The Dashboard

Goal: make the web layer useful for daily review and paper trading.

### 3.1 Improve Flask dashboard

The current Flask app is sufficient for the next stage. Do not migrate to Django yet.

Recommended dashboard sections:

- Latest metrics per symbol
- Current tags and RSI state
- Recent alerts
- Paper positions
- Closed trade history
- Portfolio equity summary
- Last poll time and service health

Target changes:

- `web/app.py`
- `web/templates/dashboard.html`
- optional `web/static/` assets

Why Flask is still the right choice now:

- The app is already wired into the agent process
- The current need is visibility, not multi-user administration
- Django would add migration overhead before strategy logic is mature

### 3.2 Add JSON endpoints for the dashboard

Expose data for polling-based updates.

Suggested endpoints:

- `/api/data`
- `/api/alerts`
- `/api/paper-positions`
- `/api/paper-trades`
- `/api/health`

Why this matters:

- Enables auto-refresh without page reloads
- Prepares the app for a more advanced frontend later

## Phase 4: Backtesting And Validation

Goal: validate strategy rules before moving closer to execution.

### 4.1 Expand backtesting beyond the demo strategy

The current backtest module is real but still minimal.

Recommended next steps:

- Separate strategy definitions from the backtest runner
- Persist results instead of only printing them
- Compare strategies by symbol and timeframe
- Add parameter configuration for RSI thresholds and ATR exits

Target changes:

- `src/backtest.py`
- new `src/strategies.py`
- optional output files in `data/`

### 4.2 Create validation reports

Track results such as:

- Win rate
- Average gain/loss
- Max drawdown
- Sharpe-like summary
- Trade count by symbol

Why this matters:

- Prevents over-trusting alerts without evidence
- Gives a path from intuition to measured strategy quality

## Phase 5: Production Readiness

Goal: run the system continuously and observe it safely.

### 5.1 Cloud deployment

Recommended target order:

1. Google Cloud Run for simplest container deployment
2. AWS ECS/Fargate if you want more infrastructure control
3. Heroku only if simplicity matters more than cost or long-term flexibility

Prerequisites before cloud rollout:

- Move secrets to cloud secret storage
- Use managed PostgreSQL instead of local SQLite
- Separate web and worker concerns if needed

Suggested deployment shape:

- one service for the agent loop
- one service for the dashboard if traffic matters
- one managed database

### 5.2 Monitoring and observability

Recommended additions:

- Structured JSON logs
- `/api/health` endpoint
- Prometheus metrics endpoint
- Grafana dashboards for uptime, poll cycles, API failures, and email failures

Target changes:

- logging setup in the application layer
- optional metrics module
- container and deployment configuration

## Phase 6: Broker And Execution Integrations

Goal: move from manual paper execution to controlled automation.

### 6.1 Manual paper trading first

Use Thinkorswim PaperMoney or another broker simulator while keeping execution manual.

Current recommended workflow:

1. Receive email alert from the agent
2. Open chart in Thinkorswim PaperMoney
3. Check the setup against a strategy playbook
4. Enter paper order manually
5. Compare platform results against the agent's recorded signal

This is the correct next step before any broker API automation.

### 6.2 Broker API later

Only after paper-trade results look consistent, consider API integration.

Candidate brokers:

- Alpaca for equities and straightforward paper API testing
- Tradier for options-friendly workflows
- Interactive Brokers for broader capabilities

Why this should come later:

- Execution without validated strategy logic increases risk
- Broker integration adds operational and compliance complexity

## Recommended Execution Order

The best sequence for this codebase is:

1. Add monitoring and observability (`/api/metrics`, structured logs, dashboard heartbeat)
2. Improve backtesting reports and parameter validation outputs
3. Split `src/utils.py` into focused modules
4. Move from SQLite to PostgreSQL
5. Deploy to cloud with proper secrets management
6. Expand runtime monitoring dashboards/alerts
7. Evaluate broker API integration after paper results are stable

## What Not To Do Yet

Avoid these moves right now:

- Migrating to Django before the workflow is mature
- Automating live trades before paper performance is measured
- Adding too many new indicators before one strategy is fully defined
- Deploying to cloud before the database and monitoring story are stable

## Immediate Next Build

If only one next feature is chosen, it should be this:

Add runtime observability: `/api/metrics` + structured signal/email logging + dashboard heartbeat for last cycle and last email result.

That adds the highest operational confidence now that strategy execution is already explicit.