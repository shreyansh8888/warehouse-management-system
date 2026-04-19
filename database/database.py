import sqlite3
import datetime

class WarehouseDB:
    def __init__(self):
        self.conn = sqlite3.connect("warehouse.db")
        self.cursor = self.conn.cursor()

        # ---------- USERS ----------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
        """)

        # ---------- INVENTORY ----------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            sku TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            quantity INTEGER,
            location TEXT,
            supplier_id INTEGER
        )
        """)

        # ---------- SUPPLIERS ----------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            contact TEXT,
            email TEXT
        )
        """)

        # ---------- SALES ----------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT,
            qty INTEGER,
            amount REAL,
            date TEXT
        )
        """)

        # ---------- LOGS ----------
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            action TEXT,
            detail TEXT
        )
        """)

        # Default admin
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                ("admin", "admin123", "admin")
            )

        self.conn.commit()

    # ================= USERS =================
    def add_user(self, u, p):
        try:
            self.cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?)", (u, p, "user")
            )
            self.conn.commit()
            return True
        except:
            return False

    def check_user(self, u, p):
        self.cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (u, p)
        )
        return self.cursor.fetchone()

    def get_users(self):
        self.cursor.execute("SELECT username, role FROM users")
        return self.cursor.fetchall()

    def delete_user(self, u):
        self.cursor.execute("DELETE FROM users WHERE username=?", (u,))
        self.conn.commit()

    def set_role(self, u, role):
        self.cursor.execute("UPDATE users SET role=? WHERE username=?", (role, u))
        self.conn.commit()

    # ================= INVENTORY =================
    def add_product(self, sku, name, cat, qty, loc, sid):
        try:
            self.cursor.execute(
                "INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)",
                (sku, name, cat, qty, loc, sid)
            )
            self.conn.commit()
            return True
        except:
            return False

    def get_inventory(self):
        self.cursor.execute("""
        SELECT i.sku, i.name, i.category, i.quantity, i.location,
               COALESCE(s.name, '-')
        FROM inventory i
        LEFT JOIN suppliers s ON i.supplier_id = s.id
        """)
        return self.cursor.fetchall()

    def get_product(self, sku):
        self.cursor.execute("SELECT * FROM inventory WHERE sku=?", (sku,))
        return self.cursor.fetchone()

    def update_product(self, sku, name, cat, qty, loc, sid):
        self.cursor.execute("""
        UPDATE inventory
        SET name=?, category=?, quantity=?, location=?, supplier_id=?
        WHERE sku=?
        """, (name, cat, qty, loc, sid, sku))
        self.conn.commit()

    def delete_product(self, sku):
        self.cursor.execute("DELETE FROM inventory WHERE sku=?", (sku,))
        self.conn.commit()

    # ================= SUPPLIERS =================
    def add_supplier(self, name, contact, email):
        try:
            self.cursor.execute(
                "INSERT INTO suppliers (name, contact, email) VALUES (?, ?, ?)",
                (name, contact, email)
            )
            self.conn.commit()
            return True
        except:
            return False

    def get_suppliers(self):
        self.cursor.execute("SELECT * FROM suppliers")
        return self.cursor.fetchall()

    def delete_supplier(self, sid):
        self.cursor.execute("DELETE FROM suppliers WHERE id=?", (sid,))
        self.conn.commit()

    # ================= SALES =================
    def add_sale(self, sku, qty, amt, dt):
        self.cursor.execute(
            "INSERT INTO sales (sku, qty, amount, date) VALUES (?, ?, ?, ?)",
            (sku, qty, amt, dt)
        )
        self.conn.commit()

    def get_sales(self):
        self.cursor.execute("""
        SELECT s.id, s.sku, i.name, s.qty, s.amount, s.date
        FROM sales s
        LEFT JOIN inventory i ON s.sku = i.sku
        ORDER BY s.id DESC
        """)
        return self.cursor.fetchall()

    def get_monthly_sales(self):
        self.cursor.execute("""
        SELECT substr(date,1,7), SUM(amount)
        FROM sales
        GROUP BY substr(date,1,7)
        """)
        return self.cursor.fetchall()

    def get_daily_sales(self):
        self.cursor.execute("""
        SELECT date, SUM(amount)
        FROM sales
        GROUP BY date
        ORDER BY date DESC LIMIT 14
        """)
        return self.cursor.fetchall()

    # ================= DASHBOARD =================
    def get_counts(self):
        self.cursor.execute("SELECT COUNT(*) FROM inventory")
        products = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM suppliers")
        suppliers = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(DISTINCT category) FROM inventory")
        categories = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(amount),0) FROM sales")
        sales = self.cursor.fetchone()[0]

        return products, suppliers, categories, sales

    def get_category_stock(self):
        self.cursor.execute("""
        SELECT category, SUM(quantity)
        FROM inventory
        GROUP BY category
        """)
        return self.cursor.fetchall()

    # ================= LOGS =================
    def log(self, user, action, detail):
        self.cursor.execute(
            "INSERT INTO logs VALUES (NULL, ?, ?, ?, ?)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             user, action, detail)
        )
        self.conn.commit()

    def get_logs(self):
        self.cursor.execute("SELECT * FROM logs ORDER BY id DESC")
        return self.cursor.fetchall()

    def delete_log(self, lid):
        self.cursor.execute("DELETE FROM logs WHERE id=?", (lid,))
        self.conn.commit()

    def clear_logs(self):
        self.cursor.execute("DELETE FROM logs")
        self.conn.commit()