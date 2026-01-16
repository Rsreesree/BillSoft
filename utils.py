"""Utility functions for BillSoft"""
import json
import os
from datetime import datetime
import sys


# Printer configuration constants
CONFIG_FILE = "printer_config.json"

# ESC/POS commands for thermal printer
ESC_INIT = b"\x1b@"
ESC_CUT = b"\x1dV\x00"
ESC_BOLD_ON = b"\x1bE\x01"
ESC_BOLD_OFF = b"\x1bE\x00"
ESC_ALIGN_CENTER = b"\x1ba\x01"
ESC_ALIGN_LEFT = b"\x1ba\x00"
ESC_ALIGN_RIGHT = b"\x1ba\x02"
ESC_DOUBLE_HEIGHT = b"\x1b!\x10"
ESC_DOUBLE_WIDTH = b"\x1b!\x20"
ESC_NORMAL_SIZE = b"\x1b!\x00"
ESC_UNDERLINE_ON = b"\x1b-\x01"
ESC_UNDERLINE_OFF = b"\x1b-\x00"
ESC_FEED_LINES = lambda n: bytes([0x1b, 0x64, n])

# Check if Windows print API is available
try:
    import win32print
    WINDOWS_PRINT_AVAILABLE = True
except ImportError:
    WINDOWS_PRINT_AVAILABLE = False


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_printing_config():
    """Load printer configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return {"method": "Browser", "printer_name": ""}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"method": "Browser", "printer_name": ""}


def save_printing_config(config):
    """Save printer configuration to file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def is_printer_online(printer_name):
    """Check if printer is online and ready"""
    if not WINDOWS_PRINT_AVAILABLE:
        return False
    try:
        handle = win32print.OpenPrinter(printer_name)
        win32print.ClosePrinter(handle)
        return True
    except:
        return False


def get_available_printers():
    """Get list of available printers"""
    if WINDOWS_PRINT_AVAILABLE:
        try:
            printers = [p[2] for p in win32print.EnumPrinters(2)]
            return printers
        except:
            return ["No printers found"]
    else:
        return ["Install pywin32 for printer support"]


def format_enhanced_receipt(cart, total, receipt_width=42):
    """Creates a beautifully formatted receipt with proper alignment"""
    lines = []
    
    # Header with centered store name
    lines.append("=" * receipt_width)
    store_name = "Billsoft"
    lines.append(store_name.center(receipt_width))
    lines.append("=" * receipt_width)
    
    # Date and time centered
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(dt.center(receipt_width))
    lines.append("-" * receipt_width)
    lines.append("")
    
    # Column headers
    header = f"{'ITEM':<20} {'QTY':>4} {'PRICE':>7} {'TOTAL':>8}"
    lines.append(header)
    lines.append("-" * receipt_width)
    
    # Items with proper alignment
    subtotal = 0
    for entry in cart:
        item_name = entry['item'][:20]  # Truncate if too long
        qty = entry['qty']
        price = entry['price']
        item_total = qty * price
        subtotal += item_total
        
        line = f"{item_name:<20} {qty:>4} {price:>7.2f} {item_total:>8.2f}"
        lines.append(line)
    
    lines.append("-" * receipt_width)
    lines.append("")
    
    # Total section
    lines.append(f"{'SUBTOTAL:':<30} {subtotal:>10.2f}")
    lines.append(f"{'TAX (0%):':<30} {0:>10.2f}")
    lines.append("=" * receipt_width)
    lines.append(f"{'TOTAL:':<30} ₹{total:>9.2f}")
    lines.append("=" * receipt_width)
    lines.append("")
    
    # Footer
    lines.append("Thank you for shopping with us!".center(receipt_width))
    lines.append("Visit us again soon!".center(receipt_width))
    lines.append("")
    lines.append("-" * receipt_width)
    lines.append("")

    return lines
