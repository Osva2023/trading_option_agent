# Next Technical Ticket: Explicit Strategy Layer v1

## Status
Completed on March 17, 2026 in branch `TA-STRAT-001`.

Key outcomes delivered:
- `src/strategies.py` created with `StrategySignal` and `evaluate_strategy(...)`.
- `src/trading_agent.py` wired to evaluate strategy and execute paper signals.
- `src/paper_trading.py` refactored to execute signals (decision logic removed).
- `tests/test_strategy_layer.py` added and passing.
- `src/backtest.py` aligned to strategy-layer signals.
- Dashboard/API status semantics split into market session vs scanner window.

## Recommended Follow-up Ticket
Ticket ID suggestion: `TA-OBS-002`

Objective:
Add operational visibility for the running agent now that strategy flow is explicit.

Scope suggestion:
- Add `/api/metrics` endpoint (cycle count, last success timestamp, recent errors, email send status).
- Add structured logging for each cycle and signal decision.
- Add dashboard heartbeat fields: last cycle time, last email result, scanner active state.

## Ticket ID
TA-STRAT-001

## Objective
Introduce an explicit strategy layer so signal generation is deterministic, testable, and reusable for both alerting and paper execution.

## Background
The agent already computes metrics, classifies tags, and supports paper trading flows. What is still missing is a clear strategy module that decides entry and exit using stable rules instead of scattered logic.

This ticket implements the first strategy in a dedicated module and wires it into the main loop.

## Scope
In scope:
- Add strategy module with one production-ready strategy.
- Define strategy output contract used by trading loop and paper engine.
- Route signal decisions through strategy layer in the main loop.
- Add tests for entry and exit scenarios.

Out of scope:
- Broker integration.
- Multi-strategy optimization.
- Dashboard redesign.

## Strategy v1
Name: rsi_mean_reversion_v1

Universe:
- SPY
- QQQ

Entry rules:
- Tag contains OVERSOLD.
- Tag does not contain TRENDING_DOWN.
- Optional confirmation: close_price >= ema50.
- No open paper position for the same symbol.

Exit rules:
- RSI recovery threshold reached (example: rsi >= 55).
- ATR stop loss hit.
- ATR target reached.

Risk defaults:
- Stop loss = entry_price - 1.0 * ATR.
- Target = entry_price + 2.0 * ATR.
- Fixed quantity per signal (configurable).

## Implementation Plan
1. Create strategy module:
- Add src/strategies.py.
- Add StrategySignal dataclass or dict schema.
- Add evaluate_strategy(symbol, metrics, tags, context) -> StrategySignal | None.

2. Centralize configuration:
- Add strategy config constants in config/settings.py:
  - STRATEGY_ENABLED
  - STRATEGY_SYMBOLS
  - RSI_ENTRY_THRESHOLD
  - RSI_EXIT_THRESHOLD
  - ATR_STOP_MULTIPLIER
  - ATR_TARGET_MULTIPLIER
  - PAPER_POSITION_SIZE

3. Wire into main loop:
- Update src/trading_agent.py.
- Evaluate strategy after metrics and tags are computed.
- If signal exists, send to paper engine and include strategy context in alert payload.

4. Tighten paper interface:
- Ensure src/paper_trading.py accepts strategy signal fields (signal_id, strategy_version, risk params).
- Keep backward compatibility for existing calls.

5. Tests:
- Add tests/test_strategy_layer.py.
- Add deterministic fixtures for metrics/tags.
- Cover at least:
  - Entry accepted.
  - Entry rejected because TRENDING_DOWN.
  - Exit by RSI recovery.
  - Exit by stop.
  - Exit by target.

## Acceptance Criteria
- Signal decisions come only from src/strategies.py for the configured symbols.
- A valid signal includes: signal_id, symbol, action, strategy, strategy_version, reason, and risk levels.
- trading_agent loop can execute at least one full open/close cycle using strategy output.
- tests/test_strategy_layer.py passes.
- Existing suite command still works:
  - ./cli.sh test

## Verification Steps
1. Run syntax and smoke tests:
- ./cli.sh test

2. Strategy-specific validation:
- Run tests/test_strategy_layer.py.

3. Manual validation:
- Start agent in test mode.
- Confirm at least one strategy decision appears in logs and alert body format.

## Risks
- Rule duplication between trading_agent and paper_trading.
- Implicit dependencies on tag naming conventions.
- Unstable behavior if metrics fields are missing.

## Mitigations
- Keep one strategy evaluator entry point.
- Validate required fields before evaluation.
- Add explicit fallback path with no signal on incomplete data.

## Deliverables
- src/strategies.py
- config/settings.py updates
- src/trading_agent.py integration
- src/paper_trading.py compatibility update (if needed)
- tests/test_strategy_layer.py

## Effort Estimate
0.5 to 1.0 day.