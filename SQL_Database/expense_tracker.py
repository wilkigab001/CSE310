"""
Expense Tracker — a simple CLI app demonstrating core SQL operations.

Requirements covered:
  BASIC
    ✓ Creates a SQLite database with tables
    ✓ Insert, modify, delete, and retrieve data
    ✓ Software builds SQL commands, submits them, and uses results

  ADDITIONAL (all three)
    ✓ Two tables with a JOIN (categories ↔ expenses)
    ✓ Two aggregate functions (SUM, AVG) to summarize spending
    ✓ Date column with date-range filtering
"""

import sqlite3
from datetime import datetime


# ── Database setup ──────────────────────────────────────────────────

def connect_db():
    """Open (or create) the database and return the connection."""
    conn = sqlite3.connect("expenses.db")
    conn.execute("PRAGMA foreign_keys = ON")      # enforce FK constraints
    return conn


def create_tables(conn):
    """Create the categories and expenses tables if they don't exist."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            date        TEXT    NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    conn.commit()


def seed_categories(conn):
    """Insert default categories if the table is empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        defaults = ["Food", "Transport", "Entertainment", "Utilities", "Other"]
        cursor.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [(name,) for name in defaults]
        )
        conn.commit()
        print("Default categories created.\n")


# ── CRUD helpers ────────────────────────────────────────────────────

def list_categories(conn):
    """Print every category and return the rows for reuse."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY id")
    rows = cursor.fetchall()
    for cat_id, name in rows:
        print(f"  {cat_id}. {name}")
    return rows


# ── 1. INSERT ───────────────────────────────────────────────────────

def add_expense(conn):
    """Prompt the user and INSERT a new expense."""
    print("\n── Add Expense ──")
    description = input("Description: ").strip()
    if not description:
        print("Description cannot be empty.")
        return

    try:
        amount = float(input("Amount ($): "))
    except ValueError:
        print("Invalid amount.")
        return

    date_str = input("Date (YYYY-MM-DD) [today]: ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    # Validate the date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    print("Categories:")
    list_categories(conn)
    try:
        category_id = int(input("Category number: "))
    except ValueError:
        print("Invalid category.")
        return

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (description, amount, date, category_id) "
        "VALUES (?, ?, ?, ?)",
        (description, amount, date_str, category_id)
    )
    conn.commit()
    print(f"Expense added (ID {cursor.lastrowid}).\n")


# ── 2. RETRIEVE / QUERY  (uses a JOIN) ─────────────────────────────

def view_expenses(conn):
    """SELECT all expenses, JOINing with categories for the name."""
    print("\n── All Expenses ──")
    cursor = conn.cursor()

    # ★ JOIN between expenses and categories
    cursor.execute("""
        SELECT e.id, e.description, e.amount, e.date, c.name
        FROM   expenses   e
        JOIN   categories  c ON e.category_id = c.id
        ORDER BY e.date DESC
    """)

    rows = cursor.fetchall()
    if not rows:
        print("No expenses recorded yet.\n")
        return

    print(f"  {'ID':<5} {'Date':<12} {'Category':<15} {'Amount':>9}  Description")
    print("  " + "-" * 65)
    for eid, desc, amt, date, cat in rows:
        print(f"  {eid:<5} {date:<12} {cat:<15} ${amt:>8.2f}  {desc}")
    print()


# ── 3. MODIFY (UPDATE) ─────────────────────────────────────────────

def update_expense(conn):
    """Let the user UPDATE an existing expense's description or amount."""
    view_expenses(conn)
    try:
        eid = int(input("Expense ID to update: "))
    except ValueError:
        print("Invalid ID.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT description, amount FROM expenses WHERE id = ?", (eid,))
    row = cursor.fetchone()
    if not row:
        print("Expense not found.")
        return

    old_desc, old_amt = row
    new_desc = input(f"New description [{old_desc}]: ").strip() or old_desc
    amt_input = input(f"New amount [{old_amt}]: ").strip()
    try:
        new_amt = float(amt_input) if amt_input else old_amt
    except ValueError:
        print("Invalid amount.")
        return

    cursor.execute(
        "UPDATE expenses SET description = ?, amount = ? WHERE id = ?",
        (new_desc, new_amt, eid)
    )
    conn.commit()
    print("Expense updated.\n")


# ── 4. DELETE ───────────────────────────────────────────────────────

def delete_expense(conn):
    """DELETE an expense by ID."""
    view_expenses(conn)
    try:
        eid = int(input("Expense ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (eid,))
    conn.commit()
    if cursor.rowcount:
        print("Expense deleted.\n")
    else:
        print("Expense not found.\n")


# ── 5. AGGREGATE FUNCTIONS (SUM & AVG) ─────────────────────────────

def spending_summary(conn):
    """Use SUM and AVG to summarize spending by category."""
    print("\n── Spending Summary ──")
    cursor = conn.cursor()

    # ★ Two aggregate functions: SUM and AVG (plus COUNT for context)
    cursor.execute("""
        SELECT c.name,
               COUNT(e.id)    AS num_expenses,
               SUM(e.amount)  AS total_spent,
               AVG(e.amount)  AS avg_expense
        FROM   categories c
        LEFT JOIN expenses e ON c.id = e.category_id
        GROUP BY c.id
        ORDER BY total_spent DESC
    """)

    rows = cursor.fetchall()
    print(f"  {'Category':<15} {'Count':>6} {'Total':>10} {'Average':>10}")
    print("  " + "-" * 45)
    for name, count, total, avg in rows:
        total = total or 0.0
        avg   = avg   or 0.0
        print(f"  {name:<15} {count:>6} ${total:>9.2f} ${avg:>9.2f}")

    # Grand totals
    cursor.execute("SELECT SUM(amount), AVG(amount) FROM expenses")
    grand_total, grand_avg = cursor.fetchone()
    grand_total = grand_total or 0.0
    grand_avg   = grand_avg   or 0.0
    print("  " + "-" * 45)
    print(f"  {'GRAND TOTAL':<15}        ${grand_total:>9.2f} ${grand_avg:>9.2f}")
    print()


# ── 6. DATE-RANGE FILTER ───────────────────────────────────────────

def filter_by_date(conn):
    """Query expenses within a user-supplied date range."""
    print("\n── Filter by Date Range ──")
    start = input("Start date (YYYY-MM-DD): ").strip()
    end   = input("End date   (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end,   "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    cursor = conn.cursor()

    # ★ Date-range filtering with a JOIN
    cursor.execute("""
        SELECT e.id, e.description, e.amount, e.date, c.name
        FROM   expenses  e
        JOIN   categories c ON e.category_id = c.id
        WHERE  e.date BETWEEN ? AND ?
        ORDER BY e.date
    """, (start, end))

    rows = cursor.fetchall()
    if not rows:
        print("No expenses found in that range.\n")
        return

    print(f"  {'ID':<5} {'Date':<12} {'Category':<15} {'Amount':>9}  Description")
    print("  " + "-" * 65)
    total = 0.0
    for eid, desc, amt, date, cat in rows:
        print(f"  {eid:<5} {date:<12} {cat:<15} ${amt:>8.2f}  {desc}")
        total += amt
    print("  " + "-" * 65)
    print(f"  Range total: ${total:.2f}\n")


# ── Main menu ───────────────────────────────────────────────────────

def main():
    conn = connect_db()
    create_tables(conn)
    seed_categories(conn)

    menu = """
    ╔══════════════════════════════╗
    ║      EXPENSE TRACKER        ║
    ╠══════════════════════════════╣
    ║  1. Add expense             ║
    ║  2. View all expenses       ║
    ║  3. Update an expense       ║
    ║  4. Delete an expense       ║
    ║  5. Spending summary        ║
    ║  6. Filter by date range    ║
    ║  7. Quit                    ║
    ╚══════════════════════════════╝
    """

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        if   choice == "1":  add_expense(conn)
        elif choice == "2":  view_expenses(conn)
        elif choice == "3":  update_expense(conn)
        elif choice == "4":  delete_expense(conn)
        elif choice == "5":  spending_summary(conn)
        elif choice == "6":  filter_by_date(conn)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

    conn.close()


if __name__ == "__main__":
    main()