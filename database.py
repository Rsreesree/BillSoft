"""Database management modules for BillSoft"""
import sqlite3
from datetime import datetime
import json
import os
import shutil
from tkinter import messagebox, filedialog


class DatabaseManager:
    """Manages inventory and sales data"""
    
    def __init__(self, db_name="Data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        self.last_receipt_table()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL,
                stock INTEGER,
                barcode TEXT UNIQUE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                date_time TEXT,
                billing_type TEXT DEFAULT 'REGULAR'
            );
        """)
        self.conn.commit()

    def last_receipt_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_receipt (
                id INTEGER PRIMARY KEY,
                cart_data TEXT,
                total REAL,
                timestamp TEXT
            );
        """)
        self.conn.commit()

    # Inventory Operations
    def add_inventory_item(self, name, price, stock, barcode):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (name, price, stock, barcode) VALUES (?, ?, ?, ?)",
                       (name, price, stock, barcode))
        self.conn.commit()

    def update_inventory_item(self, name, price, stock):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE inventory SET price=?, stock=?  WHERE name=?",
                       (price, stock, name))
        self.conn.commit()

    def delete_inventory_item(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE name=?", (name,))
        self.conn.commit()

    def fetch_inventory(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, price, stock, barcode FROM inventory")
        return cursor.fetchall()

    # Sales Operations
    def add_sale(self, item_name, quantity, price, billing_type='REGULAR'):
        total = quantity * price
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sales (item_name, quantity, price, total, date_time, billing_type) VALUES (?, ?, ?, ?, ?, ?)",
                       (item_name, quantity, price, total, dt, billing_type))
        self.conn.commit()

    def update_stock(self, item_name, new_stock):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE inventory SET stock=? WHERE name=?", (new_stock, item_name))
        self.conn.commit()

    def save_last_receipt(self, cart_data, total):
        """Save the last receipt for reprinting"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cart_json = json.dumps(cart_data)
        cursor.execute("DELETE FROM last_receipt")  # Keep only one receipt
        cursor.execute("INSERT INTO last_receipt (id, cart_data, total, timestamp) VALUES (1, ?, ?, ?)",
                       (cart_json, total, timestamp))
        self.conn.commit()

    def get_last_receipt(self):
        """Retrieve the last saved receipt"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT cart_data, total, timestamp FROM last_receipt WHERE id=1")
        row = cursor.fetchone()
        if row:
            cart_data = json.loads(row[0])
            return cart_data, row[1], row[2]
        return None, None, None
    
    def backup_database(self):
        if not os.path.exists("Data.db"):
            messagebox.showerror("Error", "Database file not found!")
            return

        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Backup", "*.db")],
            title="Save Backup As"
        )

        if not backup_path:
            return

        try:
            shutil.copy("Data.db", backup_path)
            messagebox.showinfo(
                "Backup Successful",
                f"Backup saved successfully:\n{backup_path}"
            )
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))

    def restore_database(self):
        restore_path = filedialog.askopenfilename(
            filetypes=[("Database Backup", "*.db")],
            title="Select Backup File"
        )

        if not restore_path:
            return

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "Restoring will OVERWRITE current data.\n\nContinue?"
        )

        if not confirm:
            return

        try:
            self.conn.close()
            shutil.copy(restore_path, "Data.db")
            messagebox.showinfo(
                "Restore Successful",
                "Database restored successfully.\n\nApp will restart now."
            )

            # Restart app
            import sys
            python = sys.executable
            os.execl(python, python, *sys.argv)

        except Exception as e:
            messagebox.showerror("Restore Failed", str(e))


class AuthDB:
    """Manages user authentication"""
    
    def __init__(self, db_name="users.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, username, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, self.hash_password(password))
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, self.hash_password(password))
        )
        return cursor.fetchone()
