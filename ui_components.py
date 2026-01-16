"""UI components and dialogs for BillSoft"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from tkcalendar import DateEntry
from datetime import datetime
import webbrowser
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from utils import (
    resource_path, get_printing_config, save_printing_config,
    is_printer_online, get_available_printers, format_enhanced_receipt,
    WINDOWS_PRINT_AVAILABLE, CONFIG_FILE
)

try:
    import win32print
except ImportError:
    win32print = None


class SplashScreen:
    """Splash screen with loading animation"""
    
    @staticmethod
    def show():
        import time
        splash = tk.Tk()
        splash.overrideredirect(True)
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        splash.geometry(f"{screen_width}x{screen_height}+0+0")
        splash.configure(bg="#2C3E50")

        frame = tk.Frame(splash, bg="#2C3E50")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        label_title = tk.Label(frame, text="Bill Soft", font=("Yu Gothic UI semibold", 180, "bold"), 
                              fg="#1ABC9C", bg="#2C3E50")
        label_title.pack(pady=10)

        label_version = tk.Label(frame, text="Ver 2.0", font=("Yu Gothic UI semibold", 80, "bold"), 
                                fg="#1ABC9C", bg="#2C3E50")
        label_version.pack(pady=12)

        label_loading = tk.Label(frame, text="Loading...", font=("Arial", 24), 
                                fg="white", bg="#2C3E50")
        label_loading.pack(pady=10)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("custom.Horizontal.TProgressbar",
                       troughcolor="#34495E",
                       bordercolor="#34495E",
                       background="#1ABC9C",
                       thickness=30)

        progress = ttk.Progressbar(frame, style="custom.Horizontal.TProgressbar",
                                  orient='horizontal', length=screen_width//2, mode='determinate')
        progress.pack(pady=20)

        percent_label = tk.Label(frame, text="0%", font=("Arial", 24), 
                               fg="white", bg="#2C3E50")
        percent_label.pack()

        for i in range(101):
            progress['value'] = i
            percent_label.config(text=f"{i}%")
            r = int(44 + (26-44)*i/100)
            g = int(62 + (188-62)*i/100)
            b = int(80 + (156-80)*i/100)
            color = f"#{r:02x}{g:02x}{b:02x}"
            splash.configure(bg=color)
            frame.configure(bg=color)
            label_title.configure(bg=color)
            label_version.configure(bg=color)
            label_loading.configure(bg=color)
            percent_label.configure(bg=color)
            splash.update()
            time.sleep(0.05)

        splash.destroy()


class PrinterConfigDialog:
    """Dialog for printer configuration"""
    
    @staticmethod
    def show(parent):
        top = tk.Toplevel(parent)
        top.title("Printing Settings")
        top.geometry("500x550")
        top.resizable(False, False)
        top.transient(parent)
        top.grab_set()
        top.configure(bg="#1e1e1e")

        title_frame = tk.Frame(top, bg="#2196F3", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="⚙️ Printer Configuration", 
                font=("Arial", 16, "bold"), bg="#2196F3", fg="white").pack(pady=15)

        content = tk.Frame(top, bg="#1e1e1e", padx=30, pady=20)
        content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, text="Select Printing Method:", 
                font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#FFD700").pack(anchor="w", pady=(0, 5))
        
        method_var = tk.StringVar(value=get_printing_config().get("method", "Browser"))
        method_frame = tk.Frame(content, bg="#1e1e1e")
        method_frame.pack(fill=tk.X, pady=(0, 20))
        
        methods = ["Browser", "Thermal Printer", "Windows Printer"]
        for method in methods:
            tk.Radiobutton(method_frame, text=method, variable=method_var, value=method,
                          font=("Arial", 11), bg="#1e1e1e", fg="white", 
                          selectcolor="#2196F3", activebackground="#1e1e1e",
                          activeforeground="white").pack(anchor="w", pady=2)

        tk.Label(content, text="Select Printer:", 
                font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#FFD700").pack(anchor="w", pady=(0, 5))
        
        printer_var = tk.StringVar(value=get_printing_config().get("printer_name", ""))
        printers = get_available_printers()
        
        printer_combo = ttk.Combobox(content, textvariable=printer_var, 
                                     values=printers, font=("Arial", 11), width=35)
        printer_combo.pack(fill=tk.X, pady=(0, 20))

        tk.Label(content, text="Thermal Paper Size (mm):", 
                font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#FFD700").pack(anchor="w", pady=(0, 5))
        
        size_frame = tk.Frame(content, bg="#1e1e1e")
        size_frame.pack(fill=tk.X, pady=(0, 20))
        
        config = get_printing_config()
        default_width = config.get("paper_width", 80)
        default_chars = config.get("chars_per_line", 42)
        
        tk.Label(size_frame, text="Width:", font=("Arial", 10), 
                bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky="w", padx=(0, 10))
        width_var = tk.IntVar(value=default_width)
        width_spin = tk.Spinbox(size_frame, from_=50, to=120, textvariable=width_var, 
                               font=("Arial", 10), width=10)
        width_spin.grid(row=0, column=1, padx=(0, 5))
        tk.Label(size_frame, text="mm", font=("Arial", 10), 
                bg="#1e1e1e", fg="#aaa").grid(row=0, column=2, sticky="w")
        
        tk.Label(size_frame, text="Chars/Line:", font=("Arial", 10), 
                bg="#1e1e1e", fg="white").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        chars_var = tk.IntVar(value=default_chars)
        chars_spin = tk.Spinbox(size_frame, from_=32, to=64, textvariable=chars_var, 
                               font=("Arial", 10), width=10)
        chars_spin.grid(row=1, column=1, padx=(0, 5), pady=(10, 0))
        tk.Label(size_frame, text="characters", font=("Arial", 10), 
                bg="#1e1e1e", fg="#aaa").grid(row=1, column=2, sticky="w", pady=(10, 0))
        
        preset_frame = tk.Frame(size_frame, bg="#1e1e1e")
        preset_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="w")
        
        tk.Label(preset_frame, text="Presets:", font=("Arial", 9), 
                bg="#1e1e1e", fg="#aaa").pack(side=tk.LEFT, padx=(0, 5))
        
        def set_preset(w, c):
            width_var.set(w)
            chars_var.set(c)
        
        tk.Button(preset_frame, text="58mm", command=lambda: set_preset(58, 32),
                 bg="#555", fg="white", font=("Arial", 8), padx=8, pady=2).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="80mm", command=lambda: set_preset(80, 42),
                 bg="#555", fg="white", font=("Arial", 8), padx=8, pady=2).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="112mm", command=lambda: set_preset(112, 56),
                 bg="#555", fg="white", font=("Arial", 8), padx=8, pady=2).pack(side=tk.LEFT, padx=2)
        
        def on_method_change():
            if method_var.get() == "Browser":
                printer_combo.config(state="disabled")
                width_spin.config(state="disabled")
                chars_spin.config(state="disabled")
            elif method_var.get() == "Thermal Printer":
                printer_combo.config(state="readonly")
                width_spin.config(state="normal")
                chars_spin.config(state="normal")
            else:
                printer_combo.config(state="readonly")
                width_spin.config(state="disabled")
                chars_spin.config(state="disabled")
        
        method_var.trace('w', lambda *args: on_method_change())
        on_method_change()

        def save_settings():
            method = method_var.get()
            printer_name = printer_var.get() if method != "Browser" else ""
            
            if method != "Browser" and not printer_name:
                messagebox.showwarning("Select Printer", 
                                      "Please select a printer for this method!", parent=top)
                return
            
            paper_width = width_var.get()
            chars_per_line = chars_var.get()
            
            if paper_width < 50 or paper_width > 120:
                messagebox.showwarning("Invalid Size", 
                                      "Paper width must be between 50-120mm", parent=top)
                return
            
            if chars_per_line < 32 or chars_per_line > 64:
                messagebox.showwarning("Invalid Size", 
                                      "Characters per line must be between 32-64", parent=top)
                return
            
            config = {
                "method": method,
                "printer_name": printer_name,
                "paper_width": paper_width,
                "chars_per_line": chars_per_line
            }
            
            if save_printing_config(config):
                messagebox.showinfo("Settings Saved", 
                    f"✓ Printing method: {method}\n"
                    f"✓ Printer: {printer_name or 'N/A'}\n"
                    f"✓ Paper size: {paper_width}mm ({chars_per_line} chars/line)",
                    parent=top)
                top.destroy()
            else:
                messagebox.showerror("Save Error", "Failed to save settings", parent=top)

        btn_frame = tk.Frame(top, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Button(btn_frame, text="💾 Save & Apply", command=save_settings,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=10, cursor="hand2").pack(fill=tk.X)


class HelpDialog:
    """Help and documentation dialog"""
    
    @staticmethod
    def show(parent):
        popup = tk.Toplevel(parent)
        popup.title("Help")
        popup.geometry("560x620")
        popup.resizable(False, False)
        popup.transient(parent)
        popup.grab_set()

        tk.Label(popup, text="❓ BillSoft Help", font=("Arial", 15, "bold")).pack(pady=10)

        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                   font=("Arial", 10), bg="#f0f0f0")
        help_text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=help_text_widget.yview)

        help_text = (
            "📌 BASIC BILLING\n"
            "• Stock Billing: Use this for items already added to stock\n"
            "  (Barcode or item list will be used)\n"
            "• Fast Billing: Use this ONLY for non-stock items\n"
            "  (You must manually type the item name)\n\n"
            "🧾 BILL CREATION\n"
            "• Add items → check quantity → click Print Bill\n"
            "• After printing, stock will be updated automatically\n"
            "• Use 'Last Print' to reprint the previous bill\n\n"
            "📊 DAILY SALES REPORT\n"
            "• Shows all bills created today\n"
            "• Items sold using Fast Billing are marked as 'FAST BILLING'\n"
            "• Use this report to check total sales and cash\n\n"
            "🖨 PRINTER SETTINGS\n"
            "• Select correct printer before billing\n"
            "• Choose paper width suitable for your thermal printer\n"
            "• Select character size if text looks too small or large\n\n"
            "📦 BACKUP DATABASE\n"
            "• Backup saves all your billing data safely\n"
            "• Take backup DAILY or before any changes\n"
            "• Backup file can be stored in USB / external drive\n\n"
            "♻ RESTORE DATABASE\n"
            "• Restore is used only if data is lost or system is changed\n"
            "• ALWAYS take backup before restoring\n"
            "• Restart the application after restore\n\n"
            "⚠ IMPORTANT WARNINGS\n"
            "• Do NOT use Fast Billing for stock items\n"
            "• Do NOT restore without backup\n"
            "• Do NOT close app while printing\n\n"
            "📘 HELP & SUPPORT\n"
            "• Click 'User Guide (PDF)' for full step-by-step guide\n"
            "• Contact developer for any issues or updates"
        )

        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def open_user_guide():
            pdf_path = resource_path("BillSoft_User_Guide.txt")
            if os.path.exists(pdf_path):
                webbrowser.open(pdf_path)
            else:
                messagebox.showerror("Error", "User Guide PDF not found!")

        tk.Button(btn_frame, text="📘 Open User Guide", bg="#2196F3", fg="white",
                 font=("Arial", 11, "bold"), padx=12, pady=6, command=open_user_guide).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="❌ Close", font=("Arial", 11), padx=12, pady=6,
                 command=popup.destroy).pack(side=tk.LEFT)

        contact_frame = tk.LabelFrame(popup, text="Developer Contact", 
                                     font=("Arial", 10, "bold"), padx=10, pady=8)
        contact_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(contact_frame, text="👨‍💻 Developer: Your Name / Company Name", 
                font=("Arial", 10)).pack(anchor="w")
        tk.Label(contact_frame, text="📞 Phone: +91-XXXXXXXXXX", 
                font=("Arial", 10)).pack(anchor="w")
        tk.Label(contact_frame, text="✉ Email: support@yourdomain.com", 
                font=("Arial", 10)).pack(anchor="w")


class BackupDialog:
    """Backup and restore dialog"""
    
    @staticmethod
    def show(parent, db):
        popup = tk.Toplevel(parent)
        popup.title("Backup & Restore")
        popup.geometry("350x220")
        popup.resizable(False, False)
        popup.transient(parent)
        popup.grab_set()

        tk.Label(popup, text="📦 Backup & Restore", 
                font=("Arial", 14, "bold")).pack(pady=15)

        tk.Button(popup, text="📦 Backup Database", font=("Arial", 11, "bold"),
                 bg="#4CAF50", fg="white", pady=10,
                 command=db.backup_database).pack(fill=tk.X, padx=30, pady=8)

        tk.Button(popup, text="♻ Restore Database", font=("Arial", 11, "bold"),
                 bg="#F44336", fg="white", pady=10,
                 command=db.restore_database).pack(fill=tk.X, padx=30, pady=8)


class PrintPreviewDialog:
    """Print preview dialog with receipt preview"""
    
    @staticmethod
    def show(parent, cart, total, callback):
        preview = tk.Toplevel(parent)
        preview.title("Print Preview")
        preview.geometry("500x700")
        preview.transient(parent)
        preview.grab_set()
        
        preview_frame = tk.Frame(preview, bg="white", padx=20, pady=20)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(preview_frame, text="Receipt Preview", font=("Arial", 14, "bold"), 
                bg="white").pack(pady=10)
        
        text_widget = tk.Text(preview_frame, font=("Courier", 10), bg="#f5f5f5", 
                            wrap=tk.NONE, width=50, height=30)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        receipt_lines = format_enhanced_receipt(cart, total)
        text_widget.insert("1.0", "\n".join(receipt_lines))
        text_widget.configure(state="disabled")
        
        btn_frame = tk.Frame(preview, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="Print", command=lambda: [callback(cart, total), preview.destroy()],
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=preview.destroy,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold"), 
                 padx=20, pady=8).pack(side=tk.LEFT, padx=5)


class ManualQuantityDialog:
    """Dialog for selecting quantity and price"""
    
    @staticmethod
    def show(parent, item, inventory):
        popup = tk.Toplevel(parent)
        popup.title(f"Add '{item}' to Cart")
        popup.geometry("350x220")
        popup.transient(parent)
        popup.grab_set()

        tk.Label(popup, text=f"Enter quantity and price for '{item}':", 
                font=("Arial", 12)).pack(pady=10)

        qty_var = tk.IntVar(value=1)
        price_var = tk.DoubleVar(value=inventory[item]["price"])

        tk.Label(popup, text="Quantity").pack()
        tk.Entry(popup, textvariable=qty_var, width=10, font=("Arial", 12)).pack(pady=5)

        tk.Label(popup, text="Price").pack()
        tk.Entry(popup, textvariable=price_var, width=10, font=("Arial", 12)).pack(pady=5)

        result = {"confirmed": False, "qty": 0, "price": 0}

        def confirm_entry():
            qty = qty_var.get()
            price = price_var.get()
            if qty <= 0:
                messagebox.showwarning("Warning", "Quantity must be > 0!", parent=popup)
                return
            if price < 0:
                messagebox.showwarning("Warning", "Price cannot be negative!", parent=popup)
                return
            if inventory[item]["stock"] < qty:
                messagebox.showerror("Stock Error", "Not enough stock!", parent=popup)
                return
            result["confirmed"] = True
            result["qty"] = qty
            result["price"] = price
            popup.destroy()

        tk.Button(popup, text="Add to Cart", command=confirm_entry,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        parent.wait_window(popup)
        return result


class FastBillingDialog:
    """Dialog for fast billing (manual entry)"""
    
    @staticmethod
    def show(parent, item, inventory):
        popup = tk.Toplevel(parent)
        popup.title("Fast Billing")
        popup.geometry("320x230")
        popup.transient(parent)
        popup.grab_set()

        tk.Label(popup, text=f"Item: {item}", font=("Arial", 12, "bold")).pack(pady=10)

        qty_var = tk.IntVar(value=1)
        price_var = tk.DoubleVar(value=inventory.get(item, {}).get("price", 0))

        tk.Label(popup, text="Quantity").pack()
        tk.Entry(popup, textvariable=qty_var, font=("Arial", 12), width=10).pack(pady=5)

        tk.Label(popup, text="Price").pack()
        tk.Entry(popup, textvariable=price_var, font=("Arial", 12), width=10).pack(pady=5)

        result = {"confirmed": False, "qty": 0, "price": 0}

        def confirm_fast_bill():
            qty = qty_var.get()
            price = price_var.get()

            if qty <= 0 or price <= 0:
                messagebox.showwarning("Invalid", "Quantity & Price must be positive!", parent=popup)
                return

            result["confirmed"] = True
            result["qty"] = qty
            result["price"] = price
            popup.destroy()

        tk.Button(popup, text="Add to Cart", command=confirm_fast_bill,
                 bg="#2196F3", fg="white", font=("Arial", 12, "bold")).pack(pady=15)
        
        parent.wait_window(popup)
        return result
