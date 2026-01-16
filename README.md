# BillSoft - Professional Point-of-Sale System

**A modular, enterprise-grade retail billing and inventory management solution with multi-format printing and advanced reporting.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Quick Start](#quick-start)
- [Project Architecture](#project-architecture)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

BillSoft is a comprehensive point-of-sale (POS) system designed for retail clothing shops and general retail businesses. Built with a modular architecture, it provides complete management of sales transactions, inventory operations, user authentication, and professional receipt printing. The system features a dual-billing approach (regular and fast billing) for maximum flexibility in diverse business scenarios.

### Core Capabilities
- **Shopping Module** - Item entry by barcode or manual input with real-time cart management
- **Dual Billing Modes** - Regular inventory-tracked billing and fast manual billing
- **Inventory Management** - Complete CRUD operations with barcode support and stock tracking
- **Sales Reporting** - Daily reports with date filtering and multiple export formats
- **Multi-Format Printing** - Thermal, Windows, PDF, and browser-based printing
- **User Authentication** - Secure login and registration system
- **Data Persistence** - SQLite-based database with automated backup/restore

---

## ✨ Key Features

### 1. Shopping & Billing
✅ **ENTER ITEM Section**
- Manual item entry by barcode or name
- Automatic quantity input dialog
- Price verification and adjustment
- Real-time cart updates

✅ **FAST BILLING Section**
- Quick billing for non-inventory items
- Manual price and quantity entry
- No stock deduction required
- Ideal for services or bulk items

✅ **Shopping Cart Management**
- Scrollable item list display
- Remove items before checkout
- Real-time total calculation
- Quantity adjustment capability

✅ **Checkout Processing**
- Transaction confirmation
- Receipt generation
- Print or save receipt
- Last receipt reprinting

### 2. Inventory Management
✅ **Add Items**
- Barcode entry (optional)
- Price and stock quantity
- Item name registration
- Batch add capability

✅ **Update Items**
- Search by name or barcode
- Price modification
- Stock adjustment (+/-)
- Real-time database updates

✅ **Delete Items**
- Search and confirm deletion
- Prevent accidental removal
- Automatic stock cleanup

### 3. Sales Reporting
✅ **Daily Sales Report**
- Date-based filtering with calendar picker
- Separate regular and fast billing summaries
- Item-wise sales breakdown
- Automatic grand total calculation

✅ **Report Export**
- PDF format export
- Windows printer printing
- In-app report viewing

### 4. System Management
✅ **Printer Configuration**
- Thermal printer (ESC/POS) support
- Windows standard printer support
- PDF export option
- Browser-based printing

✅ **Data Backup**
- Automatic database backup
- Timestamped backup files
- One-click restoration
- Zip format compression

✅ **Help System**
- In-app help dialog
- Feature documentation
- Quick reference guide

---

## 🏗️ Project Architecture

### System Architecture

| Module | Purpose | Key Responsibilities |
|--------|---------|----------------------|
| **main.py** | Application Entry Point | Splash screen, login window initialization, application startup |
| **app.py** | Business Logic & UI | Shopping, inventory, reports, navigation, cart management |
| **database.py** | Data Management | CRUD operations, sales tracking, user authentication, backup/restore |
| **printing.py** | Printing Engine | Multi-format receipt printing, thermal/Windows/PDF output |
| **ui_components.py** | UI Components | Dialog windows, configuration interfaces, help dialogs |
| **login.py** | Authentication UI | User registration and login interface |
| **utils.py** | Utilities & Config | Printer commands, configuration management, helpers |

### Module Specifications

#### main.py
- **Application Entry Point**
  - Initializes splash screen
  - Loads login window
  - Creates main application instance
  - Resource path handling

#### app.py - ShopApp Class
**Navigation System:**
- Daily Sales Report button (top-right)
- Shopping button (active by default)
- Inventory button
- Help button (❓)
- Settings button (⚙) for printer config
- Backup button (📦) for data management

**Shopping Page:**
- ENTER ITEM frame - Standard inventory item addition
- FAST BILLING frame - Manual item billing without inventory tracking
- Cart Items frame - Real-time cart display with scrollbar
- Checkout buttons and receipt reprinting

**Inventory Page:**
- Add Item form (Barcode, Price, Stock, Item Name)
- Update Item search and modification
- Delete Item search and removal
- Real-time inventory display table

**Sales Report Page:**
- Calendar date picker
- Report generation with detailed breakdown
- Export to PDF or print to configured printer
- Separate Regular vs Fast Billing summaries

#### database.py
**DatabaseManager Class:**
- `fetch_inventory()` - Retrieve all items from database
- `add_sale()` - Record completed transaction
- `update_stock()` - Adjust inventory quantities
- `add_item()` - Add new inventory item
- `update_item()` - Modify item details
- `delete_item()` - Remove item from inventory
- `get_sales_data()` - Retrieve sales for reporting
- `backup_database()` - Create backup file
- `restore_database()` - Restore from backup

**AuthDB Class:**
- `register_user()` - Create new user account
- `login_user()` - Authenticate user credentials
- Password hashing with security

#### printing.py
**ReceiptPrinter Class:**
- `print_receipt()` - Main receipt output function
- `print_thermal_receipt()` - ESC/POS thermal printer format
- `print_windows_receipt()` - Windows GDI printer format
- `print_to_browser()` - HTML/browser-based printing
- `save_receipt_as_pdf()` - PDF file generation
- `format_receipt()` - Receipt text formatting

#### ui_components.py
**Dialog Components:**
- `SplashScreen` - Application startup screen
- `PrinterConfigDialog` - Printer settings interface
- `BackupDialog` - Backup/restore management
- `ManualQuantityDialog` - Quantity input for items
- `FastBillingDialog` - Fast billing price/qty input
- `PrintPreviewDialog` - Preview before printing
- `HelpDialog` - Help documentation

#### login.py
**LoginWindow Class:**
- User registration form
- User login form
- Session management
- Form validation

#### utils.py
**Utility Functions:**
- `resource_path()` - Resource file location resolution
- Printer detection and initialization
- Configuration file handling
- Receipt formatting helpers

---

## Key Features

✓ **Modular Design** - Separated concerns for improved maintainability  
✓ **Multi-Format Printing** - Thermal, Windows, PDF, and browser printing  
✓ **Robust Authentication** - Secure user login and registration  
✓ **Inventory Management** - Complete product lifecycle management  
✓ **Sales Reporting** - Comprehensive transaction analytics  
✓ **Data Persistence** - Automated backup and recovery systems  
✓ **User-Friendly Interface** - Intuitive tkinter-based GUI  

---

## Project Benefits

| Benefit | Impact |
|---------|--------|
| **Maintainability** | Single-responsibility modules reduce complexity |
| **Reusability** | Components designed for cross-project integration |
| **Testability** | Independent module testing capabilities |
| **Scalability** | Extensible architecture for new features |
| **Code Quality** | Logically organized, readable codebase |
| **Development Speed** | Reduced cognitive load through separation of concerns |

---

## 🖥️ System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 7 or later |
| **Python** | 3.8 or higher |
| **RAM** | 2 GB minimum |
| **Storage** | 500 MB available space |
| **Display** | 1366x768 resolution (1920x1080 recommended) |

### Optional Hardware
- **Thermal Printer** - ESC/POS compatible (USB or Network)
- **Barcode Scanner** - USB HID-compliant scanner

---

## 📦 Installation Guide

### Step 1: Prerequisites

Ensure Python 3.8+ is installed on your system.

**Check Python version:**
```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Project Setup

Navigate to the project directory:

```bash
cd c:\Users\YourUsername\Desktop\Network
```

### Step 3: Create Virtual Environment (Recommended)

```bash
python -m venv billsoft_env
billsoft_env\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install pillow reportlab tkcalendar pywin32
```

**Or using requirements.txt:**

```bash
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
python -c "import tkinter; import PIL; import reportlab; import tkcalendar; print('All dependencies installed!')"
```

---

## 🚀 Quick Start

### Run the Application

```bash
python main.py
```

### First Time Setup

1. **Create User Account**
   - Register with username and password on login screen
   - Click "Sign Up"

2. **Configure Printer** (Optional)
   - Click Settings (⚙) button in navigation bar
   - Select printer type (Thermal, Windows, or PDF)
   - Save configuration

3. **Add Inventory Items**
   - Navigate to "Inventory" tab
   - Click "Add Item"
   - Enter: Barcode, Price, Stock, Item Name
   - Click "Add Item"

4. **Start Billing**
   - Go to "Shopping" tab
   - Scan or enter item name
   - Click "Add to Cart"
   - Click "CONFIRM" to checkout

---

## 📁 Project Structure

```
BillSoft/
├── main.py                    # Application entry point
├── app.py                     # Main application logic (POS, inventory)
├── database.py                # SQLite database management
├── utils.py                   # Utility functions and configuration
├── printing.py                # Multi-format printing engine
├── login.py                   # User authentication interface
├── ui_components.py           # Reusable UI dialogs and components
├── README.md                  # This file
│
├── printer_config.json        # Printer settings (auto-generated)
├── clothing_shop.db           # Inventory database (auto-generated)
├── users.db                   # User database (auto-generated)
│
└── assets/                    # Images and icons
    ├── settings.webp
    ├── Backup.png
    └── logo.png
```

---

## 📦 Dependencies

| Package | Purpose | Type |
|---------|---------|------|
| **tkinter** | GUI Framework | Built-in |
| **Pillow (PIL)** | Image handling | Required |
| **reportlab** | PDF generation | Required |
| **tkcalendar** | Date selection | Required |
| **sqlite3** | Database engine | Built-in |
| **pywin32** | Windows printer API | Optional |

---

## ⚙️ Configuration

### Printer Configuration
- Access via Settings (⚙) button in navigation bar
- Supports Thermal, Windows, PDF, and Browser printing
- Configuration saved in `printer_config.json`

### Database Files
- `clothing_shop.db` - Inventory and sales data
- `users.db` - User authentication data

---

## 📖 Usage Guide

### Shopping Module

**ENTER ITEM Section:**
1. Type item name or scan barcode
2. Press Enter or click "Add to Cart"
3. Enter quantity when prompted
4. Item added to shopping cart

**FAST BILLING Section:**
1. Enter item name (no barcode required)
2. Enter price and quantity
3. Click "Add to Cart"
4. No inventory deduction occurs

**Checkout:**
1. Review all cart items
2. Click "CONFIRM"
3. Select printing option
4. Receipt generated and printed

**Reprint Receipt:**
- Click "REPRINT LAST RECEIPT" to reprint previous transaction

### Inventory Management

**Add Item:**
1. Navigate to "Inventory" tab
2. Click "Add Item"
3. Fill in: Barcode, Price, Stock, Item Name
4. Click "Add Item"

**Update Item:**
1. Click "Update Item"
2. Search by item name or barcode
3. Modify price or stock (use +/- for stock changes)
4. Click "Save Changes"

**Delete Item:**
1. Click "Delete Item"
2. Enter item name or barcode
3. Confirm deletion

### Sales Reporting

1. Click "Daily Sales Report" button
2. Select date from calendar picker
3. View breakdown of sales
4. Export to PDF or print to configured printer

---

## 🔧 Troubleshooting

### Module Import Errors
```bash
pip install pillow
pip install reportlab
pip install tkcalendar
```

### Printer Not Found
1. Ensure printer is connected and powered on
2. Click Settings (⚙) button to reconfigure printer
3. Verify printer in Windows Printer Settings
4. Test print a sample receipt

### Database Issues
1. Close application
2. Delete corrupted database file
3. Click Backup (📦) → Restore
4. Select latest backup file

### Login Problems
1. Delete `users.db` to reset (you will lose user accounts)
2. Restart application
3. Create new user account

### Application Freezes
1. Check available disk space
2. Ensure database is not corrupted
3. Restart application and try again

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review module docstrings in source code
3. Verify all dependencies are properly installed
4. Test with sample data before production use

---

## 🔐 Security Notes

- Passwords are hashed using SHA-256
- SQLite database with file-based permissions
- Backups recommended for data safety
- Each user has separate login credentials
- Always backup before major operations

---

## 📈 Future Enhancements

- Advanced analytics dashboard
- Role-based access control
- Multi-location support
- REST API integration
- Cloud backup synchronization
- Mobile app companion
- Product categorization system
- Discount and promotion engine

---

**Version**: 2.0  
**Last Updated**: January 2026  
**Python Version**: 3.8+  
**Architecture**: Modular Design  

---

**Created with ❤️ for retail business efficiency**
