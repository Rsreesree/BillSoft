"""Main application logic for BillSoft"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime

from database import DatabaseManager
from utils import resource_path
from ui_components import (
    PrinterConfigDialog, HelpDialog, BackupDialog, PrintPreviewDialog,
    ManualQuantityDialog, FastBillingDialog
)
from printing import ReceiptPrinter

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ShopApp:
    """Main application class for the clothing shop POS system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BillSoft")
        self.root.state('zoomed')
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Database
        self.db = DatabaseManager()

        # Load inventory from DB
        self.inventory = {}
        try:
            for name, price, stock, barcode in self.db.fetch_inventory():
                self.inventory[name] = {"price": price, "stock": stock, "barcode": barcode}
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {e}")
            self.inventory = {}

        self.cart = []
        self.manual_qty = tk.IntVar(value=1)

        # Report data
        self.last_report_rows = []
        self.last_report_date = ""

        # Create UI
        self.create_navigation()
        self.create_shop_page()
        self.create_inventory_page()
        self.show_frame("shop")

    # ==================== Navigation ====================
    def create_navigation(self):
        """Create navigation bar"""
        nav_frame = tk.Frame(self.root, bg="#212121", height=60)
        nav_frame.pack(side=tk.TOP, fill=tk.X)
        nav_frame.pack_propagate(False)

        tk.Label(nav_frame, text="BillSoft",font=("Arial", 20, "bold"),  
                bg="#212121", fg="#00d4ff").pack(side=tk.LEFT, padx=20)

        btn_frame = tk.Frame(nav_frame, bg="#212121")
        btn_frame.pack(side=tk.RIGHT, padx=20)

        self.Daily_sales = tk.Button(btn_frame, text="Daily Sales Report", 
                                    command=self.show_sales_report,
                                    bg="#424242", fg="white", 
                                    font=("Arial", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
        self.Daily_sales.pack(side=tk.LEFT, padx=5)
        
        self.shop_btn = tk.Button(btn_frame, text="Shopping", 
                                 command=lambda: self.show_frame("shop"),
                                 bg="#4CAF50", fg="white", 
                                 font=("Arial", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
        self.shop_btn.pack(side=tk.LEFT, padx=5)

        self.inv_btn = tk.Button(btn_frame, text="Inventory", 
                                command=lambda: self.show_frame("inventory"),
                                bg="#424242", fg="white", 
                                font=("Arial", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
        self.inv_btn.pack(side=tk.LEFT, padx=5)

        self.Helper = tk.Button(btn_frame, text="❓", 
                               command=self.open_help_popup,
                               bg="#424242", fg="white", 
                               font=("Arial", 11, "bold"), padx=20, pady=10, relief=tk.FLAT)
        self.Helper.pack(side=tk.LEFT, padx=5)

        # Container for frames
        self.container = tk.Frame(self.root, bg="#1e1e1e")
        self.container.pack(fill=tk.BOTH, expand=True)
        self.frames = {}

        # Settings icon
        try:
            if PIL_AVAILABLE:
                settings_img = Image.open(resource_path("settings.webp")).resize((30, 30))
                self.settings_icon = ImageTk.PhotoImage(settings_img)
                self.settings_text = ""
            else:
                self.settings_icon = None
                self.settings_text = "⚙"
        except:
            self.settings_icon = None
            self.settings_text = "⚙"

        tk.Button(btn_frame, image=self.settings_icon if self.settings_icon else None, 
                 compound="left", text=self.settings_text,
                 command=self.select_printer_gui,
                 bg="#212121", fg="white", font=("Arial", 11, "bold"),
                 padx=10, pady=5, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Backup icon
        try:
            if PIL_AVAILABLE:
                backup_img = Image.open(resource_path("Backup.png")).resize((40, 35))
                self.backup_icon = ImageTk.PhotoImage(backup_img)
                self.backup_text = ""
            else:
                self.backup_icon = None
                self.backup_text = "📦"
        except:
            self.backup_icon = None
            self.backup_text = "📦"

        tk.Button(btn_frame, image=self.backup_icon if self.backup_icon else None,
                 text=self.backup_text, font=("Arial", 16),
                 bg="#2C2F33", fg="white", bd=0, cursor="hand2",
                 command=self.open_backup_popup).pack(side=tk.RIGHT, padx=10)

    def show_frame(self, page_name):
        """Show specific frame"""
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "shop":
            self.shop_btn.config(bg="#4CAF50")
            self.inv_btn.config(bg="#555555")
            self.update_cart_display()
            self.item_entry.focus_set()
        else:
            self.shop_btn.config(bg="#555555")
            self.inv_btn.config(bg="#4CAF50")
            self.update_inventory_display()

    def open_backup_popup(self):
        """Open backup dialog"""
        BackupDialog.show(self.root, self.db)

    def open_help_popup(self):
        """Open help dialog"""
        HelpDialog.show(self.root)

    def select_printer_gui(self):
        """Open printer configuration dialog"""
        PrinterConfigDialog.show(self.root)

    # ==================== Shopping Page ====================
    def create_shop_page(self):
        """Create shopping page UI"""
        shop_frame = tk.Frame(self.container, bg="#1e1e1e")
        shop_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["shop"] = shop_frame
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        main_frame = tk.Frame(shop_frame, padx=30, pady=20, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Manual Entry Frame
        manual_frame = tk.LabelFrame(main_frame, text="ENTER ITEM",
                                    font=("Arial", 13, "bold"), padx=15, pady=15,
                                    bg="#282c34", fg="#ca1616", labelanchor="n",
                                    highlightbackground="#282c34", highlightcolor="#ffffff",
                                    highlightthickness=4)
        manual_frame.place(relx=0, rely=0.05, height=200, width=680)

        tk.Label(manual_frame, text="ENTER ITEM", bg="#282c34", 
                fg="#ffffff", font=("Arial", 12)).place(x=15, y=20)
        self.item_entry = tk.Entry(manual_frame, font=("Arial", 12), width=28,
                                   bg="#4d4848", fg="#ffffff", insertbackground="white",
                                   highlightbackground="#2b2b2b", highlightcolor="#ffffff",
                                   highlightthickness=2, bd=0)
        self.item_entry.place(x=150, y=20)
        self.item_entry.bind("<Return>", self.on_item_entered)

        tk.Button(manual_frame, text="Add to Cart", command=self.on_item_entered,
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).place(x=220, y=70, width=200, height=35)

        # Fast Billing Frame
        fast_frame = tk.LabelFrame(main_frame, text="FAST BILLING",
                                  font=("Arial", 13, "bold"), padx=15, pady=15,
                                  bg="#282c34", fg="#ca1616", labelanchor="n",
                                  highlightbackground="#282c34", highlightcolor="#ffffff",
                                  highlightthickness=4)
        fast_frame.place(relx=0, rely=0.49, height=200, width=680)

        tk.Label(fast_frame, text="ENTER ITEM:", fg="#ffffff", 
                bg="#282c34", font=("Arial", 12)).place(x=15, y=20)
        self.fast_item_entry = tk.Entry(fast_frame, font=("Arial", 12), width=28,
                                       bg="#4d4848", fg="#ffffff", insertbackground="white",
                                       highlightbackground="#2b2b2b", highlightcolor="#ffffff",
                                       highlightthickness=2, bd=0)
        self.fast_item_entry.place(x=150, y=20)
        self.fast_item_entry.bind("<Return>", self.fast_item_entered)

        warning_label = tk.Label(fast_frame, text="Please manually enter the item name",
                                fg="#ff9800", bg="#282c34", font=("Arial", 10, "bold"))
        warning_label.place(x=160, y=50)

        info_button = tk.Label(fast_frame, text="ℹ", fg="#ffffff",
                              bg="#3a3f4b", font=("Arial", 10, "bold"),
                              width=2, cursor="hand2")
        info_button.place(x=410, y=48)
        
        tk.Button(fast_frame, text="Add to Cart", command=self.fast_item_entered,
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).place(x=220, y=90, width=200, height=35)

        # Cart Frame
        cart_frame = tk.LabelFrame(main_frame, text="Cart Items",
                                  font=("Arial", 13, "bold"), padx=15, pady=15,
                                  bg="#282c34", fg="#ca1616", labelanchor="n",
                                  highlightthickness=2)
        cart_frame.place(x=750, y=35, height=400, width=680)

        list_frame = tk.Frame(cart_frame, bg="#282c34")
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.cart_listbox = tk.Listbox(list_frame, font=("Consolas", 11), height=10,
                                       selectmode=tk.SINGLE, bd=2, bg="#1e1e1e",
                                       fg="#ffffff", highlightbackground="#4CAF50",
                                       selectbackground="#4CAF50")
        self.cart_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.cart_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_listbox.configure(yscrollcommand=scrollbar.set)

        tk.Button(cart_frame, text="Remove Selected Item", command=self.remove_from_cart,
                 bg="#f44336", fg="white", font=("Arial", 11, "bold"),
                 pady=6, cursor="hand2").pack(fill=tk.X, pady=(8, 0))

        self.total_label = tk.Label(main_frame, text="Total: ₹0.00",
                                   font=("Arial", 16, "bold"), bg="#FFC107",
                                   fg="#1e1e1e", pady=12)
        self.total_label.place(x=750, y=480, width=680)

        tk.Button(main_frame, text="CONFIRM", command=self.checkout,
                 bg="#2196F3", fg="white", font=("Arial", 14, "bold"),
                 pady=12, cursor="hand2").place(x=750, y=600, width=680)
        
        tk.Button(main_frame, text="REPRINT LAST RECEIPT", command=self.reprint_last_receipt,
                 bg="#00d4ff", fg="white", font=("Arial", 14, "bold"),
                 pady=12, cursor="hand2").place(x=0, y=600, width=680)

        # Tooltip on hover
        def show_warning(event):
            global warning_popup
            warning_popup = tk.Toplevel(fast_frame)
            warning_popup.wm_overrideredirect(True)
            x = event.widget.winfo_rootx() + 20
            y = event.widget.winfo_rooty() + 20
            warning_popup.wm_geometry(f"+{x}+{y}")
            tk.Label(warning_popup, text="FAST BILLING is for MANUAL items only.\n"
                    "• No barcode scanning\n• No stock tracking\n"
                    "• Price & quantity entered manually\n• Stock will NOT be reduced",
                    justify="left", background="#ffffe0", relief="solid",
                    borderwidth=1, font=("Arial", 9)).pack(ipadx=5, ipady=5)

        def hide_warning(event):
            global warning_popup
            if warning_popup:
                warning_popup.destroy()

        info_button.bind("<Enter>", show_warning)
        info_button.bind("<Leave>", hide_warning)
        self.warning_popup = None

    def on_item_entered(self, event=None):
        """Handle manual item entry"""
        value = self.item_entry.get().strip()
        
        if not value:
            messagebox.showwarning("Input Required", 
                "Please enter an item name or scan a barcode!")
            self.item_entry.focus_set()
            return

        # Match barcode
        for name, data in self.inventory.items():
            if data.get("barcode") == value:
                self.manual_quantity_popup(name)
                self.item_entry.delete(0, tk.END)
                return

        # Match item name
        if value in self.inventory:
            self.manual_quantity_popup(value)
            self.item_entry.delete(0, tk.END)
            return

        messagebox.showerror("Not Found", "Item or barcode not found!")
        self.item_entry.delete(0, tk.END)

    def fast_item_entered(self, event=None):
        """Handle fast billing item entry"""
        item = self.fast_item_entry.get().strip()
        if not item:
            messagebox.showwarning("Input Required", "Scan or enter item!")
            return

        self.fast_quantity_price_popup(item)
        self.fast_item_entry.delete(0, tk.END)

    def manual_quantity_popup(self, item):
        """Show popup for manual quantity and price"""
        if item not in self.inventory:
            messagebox.showerror("Error", f"'{item}' not found in inventory!")
            return

        result = ManualQuantityDialog.show(self.root, item, self.inventory)
        
        if result.get("confirmed"):
            qty = result["qty"]
            price = result["price"]
            self.add_manual_item_with_price(item, qty, price)

    def fast_quantity_price_popup(self, item):
        """Show popup for fast billing quantity and price"""
        result = FastBillingDialog.show(self.root, item, self.inventory)
        
        if result.get("confirmed"):
            qty = result["qty"]
            price = result["price"]
            
            for entry in self.cart:
                if entry["item"] == item and entry["price"] == price:
                    entry["qty"] += qty
                    self.update_cart_display()
                    return
            
            self.cart.append({"item": item, "qty": qty, "price": price, "billing_type": "FAST"})
            self.update_cart_display()
            self.fast_item_entry.focus_set()

    def add_manual_item_with_price(self, item, qty, price):
        """Add item to cart"""
        for entry in self.cart:
            if entry["item"] == item and entry["price"] == price:
                entry["qty"] += qty
                self.update_cart_display()
                return
        self.cart.append({"item": item, "qty": qty, "price": price, "billing_type": "REGULAR"})
        self.update_cart_display()

    def update_cart_display(self):
        """Update cart display"""
        self.cart_listbox.delete(0, "end")
        total = 0
        for entry in self.cart:
            subtotal = entry["qty"] * entry["price"]
            total += subtotal
            
            billing_marker = " ⚡" if entry.get("billing_type") == "FAST" else ""
            
            self.cart_listbox.insert("end", 
                f"{entry['qty']}x {entry['item']}{billing_marker} - ₹{subtotal:.2f}")
        
        self.total_label.config(text=f"Total: ₹{total:.2f}")

    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select item to remove!")
            return
        index = selection[0]
        self.cart.pop(index)
        self.update_cart_display()

    def checkout(self):
        """Process checkout"""
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        total = sum(entry["qty"] * entry["price"] for entry in self.cart)

        # Reduce stock and save sales
        for entry in self.cart:
            item = entry['item']
            qty = entry['qty']
            billing_type = entry.get('billing_type', 'REGULAR')

            if item in self.inventory and billing_type == 'REGULAR':
                self.inventory[item]['stock'] -= qty
                self.db.update_stock(item, self.inventory[item]['stock'])

            self.db.add_sale(item, qty, entry['price'], billing_type)

        # Save receipt for reprinting
        cart_copy = self.cart.copy()
        self.db.save_last_receipt(cart_copy, total)
        
        # Show preview and print
        PrintPreviewDialog.show(self.root, cart_copy, total, ReceiptPrinter.print_receipt)
        self.cart.clear()
        self.update_cart_display()

    def reprint_last_receipt(self):
        """Reprint the last receipt"""
        cart_data, total, timestamp = self.db.get_last_receipt()
        
        if not cart_data:
            messagebox.showinfo("No Receipt", "No previous receipt found to reprint.")
            return
        
        confirm = messagebox.askyesno("Reprint Receipt", 
            f"Reprint receipt from {timestamp}?\nTotal: ₹{total:.2f}")
        
        if confirm:
            PrintPreviewDialog.show(self.root, cart_data, total, ReceiptPrinter.print_receipt)

    # ==================== Sales Report ====================
    def show_sales_report(self):
        """Show sales report dialog"""
        self.Daily_sales.config(bg="#4CAF50")
        popup = tk.Toplevel(self.root)
        popup.title("Daily Sales Report")
        popup.geometry("500x350")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="Select Date:", font=("Arial", 12)).pack(pady=10)

        date_var = tk.StringVar()
        date_entry = DateEntry(popup, textvariable=date_var, date_pattern='yyyy-mm-dd',
                             font=("Arial", 12), width=15)
        date_entry.pack(pady=5)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=5)

        def generate_report():
            date_str = date_var.get().strip()
            if not date_str:
                messagebox.showwarning("Input Required", "Please select a date!")
                return

            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT item_name, quantity, price, total, date_time, billing_type
                FROM sales
                WHERE date(date_time) = ?
                ORDER BY billing_type, date_time
            """, (date_str,))
            rows = cursor.fetchall()

            report_box.delete("1.0", tk.END)

            regular_sales = []
            fast_sales = []
            regular_total = 0
            fast_total = 0

            for item_name, quantity, price, total, dt, billing_type in rows:
                if billing_type == 'FAST':
                    fast_sales.append((item_name, quantity, price, total, dt))
                    fast_total += total
                else:
                    regular_sales.append((item_name, quantity, price, total, dt))
                    regular_total += total

            # Format report with sections
            report_box.insert(tk.END, f"{'='*60}\n")
            report_box.insert(tk.END, f"  DAILY SALES REPORT - {date_str}\n")
            report_box.insert(tk.END, f"{'='*60}\n\n")

            if regular_sales:
                report_box.insert(tk.END, f"┌{'─'*58}┐\n")
                report_box.insert(tk.END, f"│ 📦 REGULAR BILLING (Stock Items)".ljust(59) + "│\n")
                report_box.insert(tk.END, f"└{'─'*58}┘\n\n")
                
                for item_name, quantity, price, total, dt in regular_sales:
                    line = f"  {item_name[:30]:<30} {quantity:>3} x ₹{price:>6.2f} = ₹{total:>7.2f}\n"
                    report_box.insert(tk.END, line)
                
                report_box.insert(tk.END, f"\n  {'-'*50}\n")
                report_box.insert(tk.END, f"  Regular Subtotal: ₹{regular_total:.2f}\n")
                report_box.insert(tk.END, f"  {'-'*50}\n\n")

            if fast_sales:
                report_box.insert(tk.END, f"┌{'─'*58}┐\n")
                report_box.insert(tk.END, f"│ ⚡ FAST BILLING (Manual Entry)".ljust(59) + "│\n")
                report_box.insert(tk.END, f"└{'─'*58}┘\n\n")
                
                for item_name, quantity, price, total, dt in fast_sales:
                    line = f"  {item_name[:30]:<30} {quantity:>3} x ₹{price:>6.2f} = ₹{total:>7.2f}\n"
                    report_box.insert(tk.END, line)
                
                report_box.insert(tk.END, f"\n  {'-'*50}\n")
                report_box.insert(tk.END, f"  Fast Billing Subtotal: ₹{fast_total:.2f}\n")
                report_box.insert(tk.END, f"  {'-'*50}\n\n")

            grand_total = regular_total + fast_total
            report_box.insert(tk.END, f"{'='*60}\n")
            report_box.insert(tk.END, f"  TOTAL SALES: ₹{grand_total:.2f}\n")
            report_box.insert(tk.END, f"  (Regular: ₹{regular_total:.2f} | Fast: ₹{fast_total:.2f})\n")
            report_box.insert(tk.END, f"{'='*60}\n")

            self.last_report_rows = rows
            self.last_report_date = date_str

        tk.Button(btn_frame, text="Generate Report", command=generate_report,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Save as PDF", 
                 command=lambda: ReceiptPrinter.save_sales_report_pdf(self.last_report_date, self.last_report_rows),
                 bg="#FF9800", fg="white", font=("Arial", 12, "bold"),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Print Report", 
                 command=lambda: ReceiptPrinter.print_sales_report(self.last_report_date, self.last_report_rows),
                 bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=5)

        report_box = tk.Text(popup, width=60, height=25)
        report_box.pack(pady=10, fill=tk.BOTH, expand=True)

        self.Daily_sales.config(bg="#555555")

    # ==================== Inventory Page ====================
    def create_inventory_page(self):
        """Create inventory management page"""
        inv_frame = tk.Frame(self.container)
        inv_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["inventory"] = inv_frame

        main_frame = tk.Frame(inv_frame, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(bg="#0cc0f1")

        tk.Label(main_frame, text="Inventory Management", 
                font=("Arial", 18, "bold"), bg="#0cc0f1", fg="#0E0C01").pack(padx=20)

        table_frame = tk.Frame(main_frame, bg="#4CAF50")
        table_frame.place_configure(x=20, y=60, width=1450, height=580)

        columns = ("Item", "Price", "Stock", "Barcode")
        self.inv_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=120)
        self.inv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.inv_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inv_tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(main_frame, text="Add Item", command=self.add_inventory_item,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=8).place(x=500, y=650)

        tk.Button(main_frame, text="Update Item", command=self.update_inventory_item,
                 bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=8).place(x=700, y=650)
        
        tk.Button(main_frame, text="Delete Item", command=self.delete_inventory_item,
                 bg="#F32121", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=8).place(x=900, y=650)
        
        self.update_inventory_display()

    def add_inventory_item(self):
        """Add new inventory item"""
        popup = tk.Toplevel(self.root)
        popup.title("Add Inventory Item")
        popup.geometry("500x500")
        popup.transient(self.root)
        popup.configure(bg="#1e1e1e")
        popup.grab_set()

        tk.Label(popup, text="Enter Item Details", font=("Arial", 14, "bold")).pack(pady=10)

        item_var = tk.StringVar()
        price_var = tk.DoubleVar(value="")
        stock_var = tk.IntVar(value="")
        barcode_var = tk.StringVar()

        tk.Label(popup, text="Barcode:", bg="#1e1e1e", fg="#FFD700",
                font=("Arial", 12, "bold")).place(x=20, y=40)
        tk.Entry(popup, textvariable=barcode_var, width=30, font=("Arial", 12),
                bg="#2b2b2b", fg="#ffffff", highlightcolor="#ffffff",
                highlightthickness=2, bd=0).place(x=100, y=70)

        tk.Label(popup, text="Price:", bg="#1e1e1e", fg="#FFD700",
                font=("Arial", 12, "bold")).place(x=20, y=110)
        tk.Entry(popup, textvariable=price_var, width=30, font=("Arial", 12),
                bg="#2b2b2b", fg="#ffffff", highlightcolor="#ffffff",
                highlightthickness=2).place(x=100, y=140)

        tk.Label(popup, text="Stock:", bg="#1e1e1e", fg="#FFD700",
                font=("Arial", 12, "bold")).place(x=20, y=180)
        tk.Entry(popup, textvariable=stock_var, width=30, font=("Arial", 12),
                bg="#2b2b2b", fg="#ffffff", highlightthickness=2).place(x=100, y=210)

        tk.Label(popup, text="Item Name:", bg="#1e1e1e", fg="#FFD700",
                font=("Arial", 12, "bold")).place(x=20, y=250)
        tk.Entry(popup, textvariable=item_var, width=30, font=("Arial", 12),
                bg="#2b2b2b", fg="#ffffff", highlightthickness=2).place(x=100, y=280)

        def confirm_add():
            item = item_var.get().strip()
            price = price_var.get()
            stock = stock_var.get()
            barcode = barcode_var.get().strip() or None

            if not item:
                messagebox.showwarning("Warning", "Please fill in all fields!", parent=popup)
                return
            if price <= 0 or stock < 0:
                messagebox.showwarning("Warning", 
                    "Price must be positive and stock non-negative!", parent=popup)
                return
            if item in self.inventory:
                messagebox.showerror("Error", 
                    "Item already exists! Use Update Item instead.", parent=popup)
                return

            self.inventory[item] = {"price": price, "stock": stock, "barcode": barcode}
            self.db.add_inventory_item(item, price, stock, barcode)
            self.update_inventory_display()
            messagebox.showinfo("Success", f"{item} added to inventory!", parent=popup)
            item_var.set("")
            price_var.set("")
            stock_var.set("")
            barcode_var.set("")

        tk.Button(popup, text="Add Item", command=confirm_add, 
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).place(x=200, y=320)

    def update_inventory_item(self):
        """Update existing inventory item"""
        popup = tk.Toplevel(self.root)
        popup.title("Update Inventory Item")
        popup.geometry("450x450")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg="#1e1e1e")

        tk.Label(popup, text="Search Here:", font=("Arial", 12, "bold"),
                bg="#1e1e1e", fg="#FFD700").pack(pady=10)
        search_var = tk.StringVar()
        search_entry = tk.Entry(popup, textvariable=search_var, width=30,
                               font=("Arial", 12))
        search_entry.pack(pady=5)
        search_entry.focus_set()

        tk.Label(popup, text="Item Name:", bg="#1e1e1e", fg="#ffffff").place(x=20, y=120)
        name_var = tk.StringVar()
        name_entry = tk.Entry(popup, textvariable=name_var, width=30,
                             font=("Arial", 12))
        name_entry.place(x=150, y=120)

        tk.Label(popup, text="Price:", bg="#1e1e1e", fg="#ffffff").place(x=20, y=200)
        price_var = tk.DoubleVar()
        price_entry = tk.Entry(popup, textvariable=price_var, width=30,
                              font=("Arial", 12))
        price_entry.place(x=150, y=200)

        tk.Label(popup, text="Stock Change (+/-):", bg="#1e1e1e",
                fg="#ffffff").place(x=20, y=280)
        stock_var = tk.IntVar()
        stock_entry = tk.Entry(popup, textvariable=stock_var, width=30,
                              font=("Arial", 12))
        stock_entry.place(x=150, y=280)

        current_item = {"name": "", "price": "", "stock": "", "barcode": ""}

        def find_item(value):
            value = value.strip()
            if not value:
                return None
            if value in self.inventory:
                return value
            for name, details in self.inventory.items():
                if details.get("barcode") == value:
                    return name
            return None

        def load_item(event=None):
            item = find_item(search_var.get())
            if not item:
                messagebox.showerror("Not Found", 
                    f"'{search_var.get()}' not found!", parent=popup)
                name_var.set("")
                price_var.set(0)
                stock_var.set(0)
                return
            current_item.update({
                "name": item,
                "price": self.inventory[item]["price"],
                "stock": self.inventory[item]["stock"],
                "barcode": self.inventory[item].get("barcode", "")
            })
            name_var.set(current_item["name"])
            price_var.set(current_item["price"])
            stock_var.set(0)

        def save_changes():
            item = current_item["name"]
            if not item:
                messagebox.showerror("Error", "Load an item first!", parent=popup)
                return

            new_name = name_var.get().strip()
            new_price = price_var.get()
            stock_change = stock_var.get()

            if new_price < 0:
                messagebox.showwarning("Invalid", 
                    "Price cannot be negative!", parent=popup)
                return

            self.inventory[item]["price"] = new_price
            self.inventory[item]["stock"] += stock_change
            if new_name != item:
                self.inventory[new_name] = self.inventory.pop(item)
                self.inventory[new_name]["barcode"] = current_item["barcode"]

            cursor = self.db.conn.cursor()
            cursor.execute("UPDATE inventory SET name=?, price=?, stock=? WHERE name=?",
                        (new_name, new_price, self.inventory[new_name]["stock"], item))
            self.db.conn.commit()

            messagebox.showinfo("Success", 
                f"'{new_name}' updated successfully!", parent=popup)
            search_var.set("")
            name_var.set("")
            price_var.set("")
            stock_var.set("")
            self.update_inventory_display()

        search_entry.bind("<Return>", load_item)
        tk.Button(popup, text="Save Changes", command=save_changes,
                 bg="#2196F3", fg="white", font=("Arial", 12, "bold")).place(x=150, y=400)

    def delete_inventory_item(self):
        """Delete inventory item"""
        popup = tk.Toplevel(self.root)
        popup.title("Delete Inventory Item")
        popup.geometry("400x200")
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(bg="#ff4d4d")

        tk.Label(popup, text="Enter Item Name or Barcode to Delete:",
                font=("Arial", 12, "bold"), bg="#ff4d4d", fg="white").pack(pady=20)
        item_var = tk.StringVar()
        item_entry = tk.Entry(popup, textvariable=item_var, font=("Arial", 12),
                             width=30)
        item_entry.pack(pady=5)
        item_entry.focus_set()

        def confirm_delete():
            value = item_var.get().strip()
            if not value:
                messagebox.showerror("Error", 
                    "Please enter item name or barcode!", parent=popup)
                return

            item_to_delete = None
            if value in self.inventory:
                item_to_delete = value
            else:
                for name, details in self.inventory.items():
                    if details.get("barcode") == value:
                        item_to_delete = name
                        break

            if not item_to_delete:
                messagebox.showerror("Error", 
                    f"Item '{value}' not found!", parent=popup)
                return

            confirm = messagebox.askyesno("Confirm Delete",
                f"Are you sure you want to delete '{item_to_delete}'?", parent=popup)
            if confirm:
                del self.inventory[item_to_delete]
                self.db.delete_inventory_item(item_to_delete)
                self.update_inventory_display()
                messagebox.showinfo("Deleted", 
                    f"'{item_to_delete}' has been deleted!", parent=popup)
                item_var.set("")
                item_entry.focus_set()

        tk.Button(popup, text="Delete Item", command=confirm_delete,
                 bg="#d50000", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

    def update_inventory_display(self):
        """Update inventory table display"""
        self.inv_tree.delete(*self.inv_tree.get_children())
        for item, details in self.inventory.items():
            self.inv_tree.insert("", "end", values=(item, f"₹{details['price']:.2f}",
                                                   details['stock'], 
                                                   details.get('barcode', '')))
