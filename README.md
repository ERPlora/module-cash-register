# Cash Register

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `cash_register` |
| **Version** | `1.0.0` |
| **Dependencies** | None |

## Models

### `CashRegisterSettings`

Per-hub cash register configuration.

| Field | Type | Details |
|-------|------|---------|
| `enable_cash_register` | BooleanField |  |
| `require_opening_balance` | BooleanField |  |
| `require_closing_balance` | BooleanField |  |
| `allow_negative_balance` | BooleanField |  |
| `auto_open_session_on_login` | BooleanField |  |
| `auto_close_session_on_logout` | BooleanField |  |
| `protected_pos_url` | CharField | max_length=200, optional |

**Methods:**

- `get_settings()`

### `CashRegister`

Physical cash register or terminal.

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=100 |
| `is_active` | BooleanField |  |

**Properties:**

- `current_session`
- `is_open`

### `CashSession`

Cash register session from opening to closing.
User-centric: one session per user.

| Field | Type | Details |
|-------|------|---------|
| `user` | ForeignKey | → `accounts.LocalUser`, on_delete=CASCADE |
| `register` | ForeignKey | → `cash_register.CashRegister`, on_delete=SET_NULL, optional |
| `session_number` | CharField | max_length=50 |
| `status` | CharField | max_length=20, choices: open, closed, suspended |
| `opened_at` | DateTimeField | optional |
| `opening_balance` | DecimalField |  |
| `opening_notes` | TextField | optional |
| `closed_at` | DateTimeField | optional |
| `closing_balance` | DecimalField | optional |
| `expected_balance` | DecimalField | optional |
| `difference` | DecimalField | optional |
| `closing_notes` | TextField | optional |

**Methods:**

- `generate_session_number()`
- `close_session()` — Close session and calculate differences.
- `get_total_sales()`
- `get_total_in()`
- `get_total_out()`
- `get_total_refunds()`
- `get_current_balance()`
- `get_duration()`
- `get_current_session()` — Get the currently open session for this user in this hub.
- `open_for_user()` — Open a new session. Reuses last closing balance if none given.

### `CashMovement`

Cash movement within a session.

| Field | Type | Details |
|-------|------|---------|
| `session` | ForeignKey | → `cash_register.CashSession`, on_delete=CASCADE |
| `movement_type` | CharField | max_length=20, choices: sale, refund, in, out |
| `amount` | DecimalField |  |
| `payment_method` | CharField | max_length=20, choices: cash, card, transfer, other |
| `sale_reference` | CharField | max_length=100, optional |
| `description` | TextField | optional |
| `employee` | ForeignKey | → `accounts.LocalUser`, on_delete=SET_NULL, optional |

**Methods:**

- `record_sale()` — Record a cash sale as a movement.

### `CashCount`

Cash denomination count at open/close.

| Field | Type | Details |
|-------|------|---------|
| `session` | ForeignKey | → `cash_register.CashSession`, on_delete=CASCADE |
| `count_type` | CharField | max_length=20, choices: opening, closing |
| `denominations` | JSONField |  |
| `total` | DecimalField |  |
| `notes` | TextField | optional |
| `counted_at` | DateTimeField | optional |

**Methods:**

- `calculate_total_from_denominations()`

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `CashSession` | `user` | `accounts.LocalUser` | CASCADE | No |
| `CashSession` | `register` | `cash_register.CashRegister` | SET_NULL | Yes |
| `CashMovement` | `session` | `cash_register.CashSession` | CASCADE | No |
| `CashMovement` | `employee` | `accounts.LocalUser` | SET_NULL | Yes |
| `CashCount` | `session` | `cash_register.CashSession` | CASCADE | No |

## URL Endpoints

Base path: `/m/cash_register/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `open/` | `open_session` | GET |
| `close/` | `close_session` | GET |
| `session/<uuid:session_id>/` | `session_detail` | GET |
| `history/` | `history` | GET |
| `settings/` | `settings` | GET |
| `register/add/` | `add_register` | GET/POST |
| `register/<uuid:register_id>/toggle/` | `toggle_register` | GET |
| `api/session/open/` | `api_open_session` | GET |
| `api/session/close/` | `api_close_session` | GET |
| `api/session/current/` | `api_current_session` | GET |
| `api/session/<uuid:session_id>/movements/` | `api_session_movements` | GET |
| `api/movement/add/` | `api_add_movement` | GET/POST |
| `htmx/calculate-denominations/` | `htmx_calculate_denominations` | GET |
| `htmx/calculate-difference/` | `htmx_calculate_difference` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `cash_register.view_session` | View Session |
| `cash_register.add_session` | Add Session |
| `cash_register.close_session` | Close Session |
| `cash_register.view_movement` | View Movement |
| `cash_register.add_movement` | Add Movement |
| `cash_register.view_count` | View Count |
| `cash_register.add_count` | Add Count |
| `cash_register.view_reports` | View Reports |
| `cash_register.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_count`, `add_movement`, `add_session`, `close_session`, `view_count`, `view_movement`, `view_reports`, `view_session`
- **employee**: `add_count`, `add_movement`, `add_session`, `close_session`, `view_count`, `view_movement`, `view_session`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| History | `time-outline` | `history` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_cash_sessions`

List cash register sessions (open/closed). Shows opening/closing balances, differences.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter: open, closed, suspended |
| `limit` | integer | No | Max results (default 20) |

### `get_cash_session_summary`

Get summary of a cash session: total sales, cash in/out, refunds.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Cash session ID |

### `list_cash_registers`

List cash registers.

### `create_cash_register`

Create a new cash register.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Register name (e.g., 'Caja 1') |

## File Structure

```
CHANGELOG.md
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
  translate.py
middleware.py
migrations/
  0001_initial.py
  __init__.py
models.py
models_old.py
module.py
static/
  icons/
    icon.svg
    ion/
templates/
  cash_register/
    pages/
      close_session.html
      history.html
      index.html
      open_session.html
      session_detail.html
      settings.html
    partials/
      close_session_content.html
      dashboard_content.html
      history_content.html
      open_session_content.html
      session_detail_content.html
      settings_content.html
      tabbar_cash_register.html
tests/
  __init__.py
  test_models.py
  test_views.py
urls.py
views.py
```
