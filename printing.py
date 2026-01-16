"""Printing functionality for BillSoft"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import tempfile
import webbrowser
from utils import (
    format_enhanced_receipt, get_printing_config, is_printer_online,
    ESC_INIT, ESC_CUT, ESC_BOLD_ON, ESC_BOLD_OFF, ESC_ALIGN_CENTER,
    ESC_ALIGN_LEFT, ESC_DOUBLE_HEIGHT, ESC_NORMAL_SIZE, ESC_FEED_LINES,
    WINDOWS_PRINT_AVAILABLE
)

try:
    import win32print
except ImportError:
    win32print = None


class ReceiptPrinter:
    """Handles receipt printing in different formats"""
    
    @staticmethod
    def print_receipt(cart, total, parent=None):
        """Print receipt using configured method"""
        try:
            if not cart:
                messagebox.showwarning("Empty Cart", "Cart is empty!")
                return False

            method, printer_name = ReceiptPrinter.get_printing_method()

            if method == "Browser":
                return ReceiptPrinter.print_to_browser(cart, total)

            if not printer_name:
                messagebox.showerror("No Printer", 
                    "No printer selected. Please configure printer in settings.")
                return False

            if not is_printer_online(printer_name):
                messagebox.showerror("Printer Offline", 
                    f"Printer '{printer_name}' is offline")

            if method == "Thermal Printer":
                return ReceiptPrinter.print_thermal_receipt(printer_name, cart, total)
            else:
                return ReceiptPrinter.print_windows_receipt(printer_name, cart, total)

        except Exception as e:
            error_msg = f"Printing failed: {str(e)}\n\nWould you like to save as PDF instead?"
            if messagebox.askyesno("Print Error", error_msg):
                ReceiptPrinter.save_receipt_as_pdf(cart, total)
            return False

    @staticmethod
    def print_to_browser(cart, total):
        """Print receipt using browser"""
        receipt_lines = format_enhanced_receipt(cart, total)
        
        html_content = """
        <html>
        <head>
            <title>Receipt</title>
            <style>
                body {
                    font-family: 'Courier New', monospace;
                    max-width: 400px;
                    margin: 20px auto;
                    padding: 20px;
                    background: white;
                }
                pre {
                    font-size: 12px;
                    line-height: 1.4;
                }
                @media print {
                    body { margin: 0; padding: 10px; }
                }
            </style>
        </head>
        <body>
            <pre>""" + "\n".join(receipt_lines) + """</pre>
            <script>
                window.onload = function() {
                    window.print();
                }
            </script>
        </body>
        </html>
        """
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", 
                                               mode="w", encoding="utf-8")
        temp_file.write(html_content)
        temp_file.close()
        webbrowser.open(f"file://{temp_file.name}")
        return True

    @staticmethod
    def print_thermal_receipt(printer_name, cart, total):
        """Print enhanced thermal receipt with formatting"""
        if not win32print:
            messagebox.showerror("Error", "win32print not available")
            return False
            
        try:
            hPrinter = win32print.OpenPrinter(printer_name)
            
            try:
                win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                
                win32print.WritePrinter(hPrinter, ESC_INIT)
                
                # Store name - Bold, Double Height, Centered
                win32print.WritePrinter(hPrinter, ESC_ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, ESC_BOLD_ON)
                win32print.WritePrinter(hPrinter, ESC_DOUBLE_HEIGHT)
                win32print.WritePrinter(hPrinter, b"BillSoft\n")
                win32print.WritePrinter(hPrinter, ESC_NORMAL_SIZE)
                win32print.WritePrinter(hPrinter, ESC_BOLD_OFF)
                
                win32print.WritePrinter(hPrinter, ESC_ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, b"=" * 42 + b"\n")
                
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                win32print.WritePrinter(hPrinter, dt.encode('utf-8') + b"\n")
                win32print.WritePrinter(hPrinter, b"-" * 42 + b"\n\n")
                
                win32print.WritePrinter(hPrinter, ESC_ALIGN_LEFT)
                win32print.WritePrinter(hPrinter, ESC_BOLD_ON)
                header = f"{'ITEM':<20} {'QTY':>4} {'PRICE':>7} {'TOTAL':>8}\n"
                win32print.WritePrinter(hPrinter, header.encode('utf-8'))
                win32print.WritePrinter(hPrinter, ESC_BOLD_OFF)
                win32print.WritePrinter(hPrinter, b"-" * 42 + b"\n")
                
                for entry in cart:
                    item_name = entry['item'][:20]
                    qty = entry['qty']
                    price = entry['price']
                    item_total = qty * price
                    
                    line = f"{item_name:<20} {qty:>4} {price:>7.2f} {item_total:>8.2f}\n"
                    win32print.WritePrinter(hPrinter, line.encode('utf-8'))
                
                win32print.WritePrinter(hPrinter, b"-" * 42 + b"\n\n")
                
                win32print.WritePrinter(hPrinter, ESC_ALIGN_LEFT)
                subtotal_line = f"{'SUBTOTAL:':<30} {total:>10.2f}\n"
                win32print.WritePrinter(hPrinter, subtotal_line.encode('utf-8'))
                
                win32print.WritePrinter(hPrinter, b"=" * 42 + b"\n")
                win32print.WritePrinter(hPrinter, ESC_BOLD_ON)
                win32print.WritePrinter(hPrinter, ESC_DOUBLE_HEIGHT)
                total_line = f"TOTAL: Rs{total:>10.2f}\n"
                win32print.WritePrinter(hPrinter, total_line.encode('utf-8'))
                win32print.WritePrinter(hPrinter, ESC_NORMAL_SIZE)
                win32print.WritePrinter(hPrinter, ESC_BOLD_OFF)
                win32print.WritePrinter(hPrinter, b"=" * 42 + b"\n\n")
                
                win32print.WritePrinter(hPrinter, ESC_ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, b"Thank you for shopping with us!\n")
                win32print.WritePrinter(hPrinter, b"Visit us again soon!\n\n")
                
                win32print.WritePrinter(hPrinter, ESC_FEED_LINES(3))
                win32print.WritePrinter(hPrinter, ESC_CUT)
                
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
                
                return True
                
            finally:
                win32print.ClosePrinter(hPrinter)
                
        except Exception as e:
            messagebox.showerror("Printing Error", f"Failed to print: {str(e)}")
            return False

    @staticmethod
    def print_windows_receipt(printer_name, cart, total):
        """Print receipt to Windows printer"""
        if not win32print:
            messagebox.showerror("Error", "win32print not available")
            return False
            
        try:
            receipt_lines = format_enhanced_receipt(cart, total)
            
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, "\n".join(receipt_lines).encode("utf-8"))
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            
            return True
        except Exception as e:
            messagebox.showerror("Printing Error", str(e))
            return False

    @staticmethod
    def print_sales_report(date_str, rows, parent=None):
        """Print sales report"""
        if not rows:
            messagebox.showinfo("No Data", f"No sales found for {date_str}")
            return False

        report_lines = [
            "      BillSoft",
            "   Daily Sales Report",
            f"        {date_str}",
            "="*32
        ]
        total_sum = 0
        for item_name, quantity, price, total, dt, billing_type in rows:
            line = f"{item_name[:15]:15} {quantity:>3} x {price:>5.2f} = {total:>6.2f}"
            report_lines.append(line)
            total_sum += total
        report_lines += [
            "="*32,
            f"TOTAL SALES: {total_sum:.2f}",
            "="*32,
            "\n\n"
        ]

        try:
            method, printer_name = ReceiptPrinter.get_printing_method()

            if method == "Browser":
                html_content = "<html><head><title>Sales Report</title></head><body style='font-family: monospace;'><pre>"
                html_content += "\n".join(report_lines)
                html_content += "</pre><script>window.onload=function(){window.print();}</script></body></html>"

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", 
                                                       mode="w", encoding="utf-8")
                temp_file.write(html_content)
                temp_file.close()
                webbrowser.open(f"file://{temp_file.name}")
                return True

            if not printer_name:
                messagebox.showerror("No Printer", 
                    "No printer selected in the app. Set printer via 'Change Printer'.")
                return False

            if not is_printer_online(printer_name):
                messagebox.showerror("Printer Offline", 
                    f"Printer '{printer_name}' is offline.")
                return False

            if not win32print:
                messagebox.showerror("Error", "win32print not available")
                return False

            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(hPrinter, 1, ("Sales Report", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, ESC_INIT)
                win32print.WritePrinter(hPrinter, "\n".join(report_lines).encode("utf-8"))
                if method == "Thermal Printer":
                    win32print.WritePrinter(hPrinter, ESC_CUT)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)

            messagebox.showinfo("Printed", f"Sales report sent to {method} printer!")
            return True

        except Exception as e:
            messagebox.showerror("Printing Error", str(e))
            return False

    @staticmethod
    def save_receipt_as_pdf(cart, total):
        """Save receipt as PDF"""
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 50, "Receipt")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.line(50, height - 90, width - 50, height - 90)

        y = height - 120
        for entry in cart:
            item_name = entry['item']
            qty = entry['qty']
            price = entry['price']
            item_total = qty * price
            c.drawString(50, y, f"{item_name}: {qty} x ₹{price:.2f} = ₹{item_total:.2f}")
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

        c.line(50, y - 10, width - 50, y - 10)
        c.drawString(50, y - 30, f"TOTAL: ₹{total:.2f}")

        c.save()
        messagebox.showinfo("Success", f"Receipt saved as {file_path}")

    @staticmethod
    def save_sales_report_pdf(date_str, rows):
        """Save sales report as PDF"""
        if not rows:
            messagebox.showinfo("No Data", f"No sales found for {date_str}")
            return

        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Sales Report As"
        )
        if not file_path:
            return

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 50, "Daily Sales Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Date: {date_str}")
        c.line(50, height - 90, width - 50, height - 90)

        y = height - 120
        total_sum = 0
        for item_name, quantity, price, total, dt, billing_type in rows:
            tag = " [FAST]" if billing_type == "FAST" else ""
            c.drawString(50, y, f"{item_name}{tag}: {quantity} x ₹{price:.2f} = ₹{total:.2f}")
            total_sum += total
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50

        c.line(50, y - 10, width - 50, y - 10)
        c.drawString(50, y - 30, f"TOTAL SALES: ₹{total_sum:.2f}")

        c.save()
        messagebox.showinfo("Success", f"Sales report saved as {file_path}")

    @staticmethod
    def get_printing_method():
        """Get current printing method and printer name"""
        config = get_printing_config()
        return config.get("method", "Thermal Printer"), config.get("printer_name")
