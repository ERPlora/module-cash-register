"""
AI context for the Cash Register module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Cash Register

### Models
**CashRegister** — Physical terminal/register device.
- `name`, `is_active`
- `current_session`: active CashSession (if open)

**CashSession** — One shift/session from open to close. One session per user.
- `user` → accounts.LocalUser, `register` → CashRegister (optional)
- `session_number`: auto-generated (CS-INITIALS-TIMESTAMP)
- `status`: open | closed | suspended
- `opening_balance` (float in register at open)
- `closing_balance` (counted at close), `expected_balance` (calculated), `difference`
- `opened_at`, `closed_at`
- `opening_notes`, `closing_notes`

**CashMovement** — Each money flow within a session.
- `session` → CashSession (FK, related_name='movements')
- `movement_type`: sale | refund | in | out
- `amount`: positive for in/sale, negative for out/refund
- `payment_method`: cash | card | transfer | other
- `sale_reference`: sale number for traceability
- `employee` → accounts.LocalUser

**CashCount** — Denomination breakdown at open/close.
- `session` → CashSession, `count_type`: opening | closing
- `denominations` (JSONField): {"bills": {"50": 2, "20": 5}, "coins": {"2": 10, "1": 20}}
- `total`: auto-calculated from denominations

### Session lifecycle
1. Open session: CashSession.open_for_user(hub_id, user, opening_balance)
   - If session already open → returns existing
   - Reuses last closing_balance if opening_balance not specified
2. During session: movements added for each sale/refund/cash-in/cash-out
3. Close session: session.close_session(closing_balance)
   - expected_balance = opening_balance + sum(movements)
   - difference = closing_balance - expected_balance (negative = shortage)

### Balance calculation
`get_current_balance()` = opening_balance + sum(all movement amounts)
- Sales: +amount (positive)
- Refunds: -amount (negative)
- Cash in: +amount (positive)
- Cash out: -amount (negative)

### Settings (CashRegisterSettings)
- `require_opening_balance`: force cash count at open
- `require_closing_balance`: force cash count at close (default True)
- `allow_negative_balance`
- `auto_open_session_on_login` (default True)
- `auto_close_session_on_logout` (default True)
- `protected_pos_url`: URL that requires open session (default /m/sales/pos/)

### Relationships
- CashSession → CashMovement (all money flows)
- CashSession → CashCount (denomination records)
- CashMovement.sale_reference → sales.Sale.sale_number
"""

SOPS = [
    {
        "id": "open_shift",
        "triggers": {
            "es": ["abrir turno", "abrir caja", "empezar día", "iniciar turno", "empezar turno"],
            "en": ["open shift", "start day", "open register", "start shift", "begin shift"],
        },
        "description": {"es": "Abrir turno de trabajo", "en": "Open work shift"},
        "steps": [
            {"tool": "open_cash_session", "description": "Open cash register with starting balance"},
            {"tool": "get_sales_summary", "args": {"period": "yesterday"}, "description": "Review yesterday's sales"},
            {"tool": "list_reservations", "args": {"date": "today"}, "description": "Check today's reservations"},
        ],
        "modules_required": ["cash_register"],
    },
    {
        "id": "close_shift",
        "triggers": {
            "es": ["cerrar turno", "cerrar caja", "terminar día", "arqueo", "cuadrar caja"],
            "en": ["close shift", "close register", "end day", "cash count", "balance register"],
        },
        "description": {"es": "Cerrar turno y arqueo de caja", "en": "Close shift and cash count"},
        "steps": [
            {"tool": "get_cash_session_summary", "description": "Get current session summary with expected vs actual"},
            {"tool": "close_cash_session", "description": "Close session with final cash count"},
            {"tool": "get_sales_summary", "args": {"period": "today"}, "description": "Review today's sales total"},
        ],
        "modules_required": ["cash_register"],
    },
]
