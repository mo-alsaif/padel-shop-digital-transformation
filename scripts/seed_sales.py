"""
Padel shop sales generator for Odoo 18.
Creates ~65 confirmed sales orders spread over the last 6 months,
so the dashboard has realistic trends to show.

AI-assisted script: written with Claude, run and tested by me against my own Odoo instance.

Run from the repository folder (the password is asked for privately, not typed into the command):
  read -s -p "Odoo password: " PW; echo
  docker compose exec -T -e ODOO_LOGIN="you@email.com" -e ODOO_PASSWORD="$PW" odoo python3 - < scripts/seed_sales.py
"""
import os
import random
import xmlrpc.client
from datetime import datetime

URL = "http://localhost:8069"
DB = os.environ.get("ODOO_DB", "padelshop")
LOGIN = os.environ.get("ODOO_LOGIN")
PASSWORD = os.environ.get("ODOO_PASSWORD")

if not LOGIN or not PASSWORD:
    raise SystemExit("Missing ODOO_LOGIN or ODOO_PASSWORD. Check the command.")

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, LOGIN, PASSWORD, {})
if not uid:
    raise SystemExit("Login failed. Check the email/password (same as your Odoo login) and database name.")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)


def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kwargs)


# --- Look up products and customers created by the CSV imports ---
products = call("product.product", "search_read", [["default_code", "!=", False]],
                fields=["id", "default_code"])
pid = {p["default_code"]: p["id"] for p in products}

clubs = [c["id"] for c in call("res.partner", "search_read",
                               [["is_company", "=", True], ["email", "ilike", ".example"]],
                               fields=["id"])]
players = [c["id"] for c in call("res.partner", "search_read",
                                 [["is_company", "=", False], ["email", "ilike", "@example.com"]],
                                 fields=["id"])]

print(f"Found {len(pid)} products, {len(clubs)} clubs, {len(players)} players")
if len(pid) < 20 or not clubs or not players:
    raise SystemExit("Products or customers missing. Make sure both CSV imports finished.")

# --- What each type of customer usually buys: (code, weight, (min qty, max qty)) ---
PLAYER_BASKET = [
    ("BAL-001", 30, (1, 4)), ("BAL-002", 15, (1, 3)), ("ACC-001", 25, (1, 3)),
    ("ACC-002", 8, (1, 2)), ("ACC-005", 8, (1, 2)), ("APP-001", 10, (1, 2)),
    ("APP-002", 8, (1, 2)), ("APP-003", 6, (1, 1)), ("APP-004", 6, (1, 1)),
    ("SHO-001", 5, (1, 1)), ("SHO-002", 4, (1, 1)), ("RKT-006", 6, (1, 1)),
    ("RKT-001", 3, (1, 1)), ("RKT-002", 2, (1, 1)), ("RKT-003", 3, (1, 1)),
    ("RKT-004", 2, (1, 1)), ("RKT-005", 3, (1, 1)), ("ACC-003", 3, (1, 1)),
    ("ACC-004", 4, (1, 1)), ("SRV-001", 6, (1, 1)), ("SRV-002", 5, (1, 4)),
]
CLUB_BASKET = [
    ("BAL-003", 30, (1, 4)), ("BAL-001", 15, (10, 30)), ("RKT-006", 15, (4, 12)),
    ("ACC-001", 15, (10, 30)), ("APP-004", 8, (10, 30)), ("APP-001", 8, (10, 25)),
    ("RKT-003", 4, (2, 4)),
]

# --- Orders per month: quieter in the summer heat, busier as padel season starts ---
today = datetime.now()
MONTHS = [  # (year, month, number of orders)
    (2026, 6, 8), (2026, 7, 6), (2026, 8, 7),
    (2026, 9, 12), (2026, 10, 18), (2026, 11, 14),
]
DAYS_IN = {6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30}

random.seed(7)


def pick_lines(basket):
    n = random.randint(1, 3)
    chosen = set()
    lines = []
    while len(lines) < n:
        code, _, (lo, hi) = random.choices(basket, weights=[b[1] for b in basket])[0]
        if code in chosen:
            continue
        chosen.add(code)
        lines.append([0, 0, {"product_id": pid[code], "product_uom_qty": random.randint(lo, hi)}])
    return lines


created = 0
for year, month, count in MONTHS:
    last_day = DAYS_IN[month]
    if year == today.year and month == today.month:
        last_day = max(1, today.day - 1)
    for _ in range(count):
        is_club = random.random() < 0.2
        partner = random.choice(clubs if is_club else players)
        lines = pick_lines(CLUB_BASKET if is_club else PLAYER_BASKET)
        order_date = datetime(year, month, random.randint(1, last_day),
                              random.randint(9, 22), random.randint(0, 59))

        so_id = call("sale.order", "create", {"partner_id": partner, "order_line": lines})
        call("sale.order", "action_confirm", [so_id])
        # Confirming stamps today's date, so set the real order date afterwards
        call("sale.order", "write", [so_id], {"date_order": order_date.strftime("%Y-%m-%d %H:%M:%S")})
        created += 1
        print(f"  {created:>3}. order on {order_date:%Y-%m-%d} ({'club' if is_club else 'player'})")

print(f"\nDone! Created {created} confirmed sales orders.")
