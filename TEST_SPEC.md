# Test Spec: Cash Register

## Pages
- Dashboard: /m/cash_register/ — Current session status, balance, recent movements
- Open Session: /m/cash_register/open/ — Open new cash session form
- Close Session: /m/cash_register/close/ — Close current session with balance
- Session Detail: /m/cash_register/<session_id>/ — Session with all movements
- History: /m/cash_register/history/ — Past sessions list
- Settings: /m/cash_register/settings/ — CashRegisterSettings toggles + register management

## CRUD Operations

### CashRegister (physical device)
- Create: Settings page -> POST /m/cash_register/register/add/ with name*, is_active
- Toggle: POST /m/cash_register/register/<register_id>/toggle/ -> toggle is_active

### CashSession
- Create (Open): POST /m/cash_register/open/ or API POST /m/cash_register/api/session/open/ with opening_balance (optional if not required), notes -> session_number auto-generated CS-INITIALS-TIMESTAMP, status=open, waiter=current user
- Read: GET /m/cash_register/<session_id>/ -> session with movements, balance calculations
- Close: POST /m/cash_register/close/ or API POST /m/cash_register/api/session/close/ with closing_balance*, notes -> calculates expected_balance and difference -> status=closed
- Current: GET /m/cash_register/api/session/current/ -> JSON with current open session or null

### CashMovement
- Create: API POST /m/cash_register/api/movement/add/ with movement_type (in|out), amount*, description -> adds to current session
- Read: GET /m/cash_register/api/session/<session_id>/movements/ -> JSON list

### CashCount (denomination breakdown)
- HTMX: POST /m/cash_register/htmx/calculate-denominations/ -> calculate total from bill/coin counts
- HTMX: POST /m/cash_register/htmx/calculate-difference/ -> compare counted vs expected

## Business Logic

1. **Open cash session**: POST open/ with opening_balance=100.00 -> CashSession created (status=open, session_number=CS-XX-TIMESTAMP) -> table status=occupied
2. **Cash sale movement**: Sale completed with payment_method=cash -> CashMovement created (type=sale, amount=+total)
3. **Cash refund movement**: Refund processed -> CashMovement created (type=refund, amount=-total)
4. **Manual cash in**: POST movement/add with type=in, amount=50 -> CashMovement(type=in, amount=+50)
5. **Manual cash out**: POST movement/add with type=out, amount=30 -> CashMovement(type=out, amount=-30)
6. **Balance calculation**: current_balance = opening_balance + sum(all movements). Sales: +amount. Refunds: -amount. Cash in: +amount. Cash out: -amount.
7. **Close session with count**: POST close/ with closing_balance=450.00 -> expected_balance calculated -> difference = closing_balance - expected_balance. Negative = shortage, positive = overage.
8. **Denomination counting**: At open/close, denomination breakdown: bills (500, 200, 100, 50, 20, 10, 5) + coins (2, 1, 0.50, 0.20, 0.10, 0.05, 0.02, 0.01) -> total auto-calculated
9. **Auto-open on login**: If auto_open_session_on_login=True -> session opens automatically when employee logs in
10. **Auto-close on logout**: If auto_close_session_on_logout=True -> session closes automatically on logout
11. **Protected POS URL**: If enabled, navigating to POS URL without open session -> redirect to open session page
12. **Session history**: History page shows all past sessions with duration, totals, differences

## Cross-Module Interactions

### With sales
- Cash sale completion creates CashMovement (type=sale) in current session
- Cash refund creates CashMovement (type=refund)
- If require_opening_balance and no open session, POS may be restricted

### With pos
- POS may require open cash session (if protected_pos_url configured)
- Cash drawer opens on cash sale if PaymentMethod.opens_cash_drawer=True

## Settings
- enable_cash_register: Master toggle
- require_opening_balance: When True, must enter opening_balance to open session
- require_closing_balance: When True, must enter closing_balance to close session
- allow_negative_balance: When True, balance can go below 0. When False, cash out fails if would go negative.
- auto_open_session_on_login: Auto-open session on employee login
- auto_close_session_on_logout: Auto-close session on employee logout
- protected_pos_url: URL that requires open session (default /m/sales/pos/)

## Permissions
- Sessions: view_session, add_session, close_session
- Movements: view_movement, add_movement
- Counts: view_count, add_count
- Reports & Settings: view_reports, manage_settings

## Edge Cases
- Open session when one already open -> should fail or close previous?
- Close already-closed session -> should fail
- Add movement to closed session -> should fail
- Negative opening_balance -> should fail
- Session with no movements -> expected_balance = opening_balance, difference = closing - opening
- Empty history: no sessions -> show empty state
- Denomination count that doesn't match closing_balance -> should warn
- Session duration spanning midnight -> still shows correct duration
