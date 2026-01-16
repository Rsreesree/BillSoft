"""Login and authentication UI for BillSoft"""
import tkinter as tk
from tkinter import messagebox
from database import AuthDB
from app import ShopApp


class LoginWindow:
    """Login and signup window"""
    
    def __init__(self):
        self.db = AuthDB()
        self.root = tk.Tk()
        self.root.title("BillSoft Login")
        self.root.state('zoomed')
        self.root.configure(bg="#0a0a15")

        self.marquee_text = "Bill_Soft_Ver2.0"
        self.marquee_label = tk.Label(
            self.root, text=self.marquee_text, font=("HP Simplified", 68, "bold"),
            fg="#00d4ff", bg="#0a0a15"
        )
        self.marquee_label.place(x=450, y=40)

        card_width = 450
        card_height = 520

        self.container = tk.Frame(self.root, bg="#1a1a2e", bd=0)
        self.container.place(relx=0.5, rely=0.55, anchor="center",
                            width=card_width, height=card_height)

        self.show_login()
        self.root.mainloop()

    def clear(self):
        """Clear container widgets"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        """Show login form"""
        self.clear()
        
        tk.Label(self.container, text="🔐 LOGIN", font=("Segoe UI", 26, "bold"),
                bg="#1a1a2e", fg="#00d4ff").pack(pady=(40, 10))
        
        tk.Label(self.container, text="Welcome back! Please login to continue",
                font=("Segoe UI", 11), bg="#1a1a2e", fg="#888").pack(pady=(0, 30))

        tk.Label(self.container, text="Username", font=("Segoe UI", 10),
                bg="#1a1a2e", fg="#fff", anchor="w").pack(fill="x", padx=50, pady=(10, 5))
        
        self.username = tk.Entry(self.container, font=("Segoe UI", 13),
                                bg="#16213e", fg="white", insertbackground="#00d4ff",
                                bd=0, relief=tk.FLAT)
        self.username.pack(ipady=12, fill="x", padx=50, pady=5)

        tk.Label(self.container, text="Password", font=("Segoe UI", 10),
                bg="#1a1a2e", fg="#fff", anchor="w").pack(fill="x", padx=50, pady=(15, 5))
        
        self.password = tk.Entry(self.container, font=("Segoe UI", 13),
                                bg="#16213e", fg="white", insertbackground="#00d4ff",
                                bd=0, show="●", relief=tk.FLAT)
        self.password.pack(ipady=12, fill="x", padx=50, pady=5)

        login_btn = tk.Button(self.container, text="LOGIN", command=self.login,
                            bg="#00d4ff", fg="#000", font=("Segoe UI", 13, "bold"),
                            bd=0, cursor="hand2", relief=tk.FLAT)
        login_btn.pack(fill="x", padx=50, pady=(30, 10), ipady=12)

        tk.Button(self.container, text="Create new account →", command=self.show_signup,
                bg="#1a1a2e", fg="#00d4ff", font=("Segoe UI", 11),
                bd=0, cursor="hand2", relief=tk.FLAT).pack(pady=10)

    def show_signup(self):
        """Show signup form"""
        self.clear()
        
        tk.Label(self.container, text="✨ CREATE ACCOUNT", font=("Segoe UI", 24, "bold"),
                bg="#1a1a2e", fg="#00d4ff").pack(pady=(40, 10))
        
        tk.Label(self.container, text="Sign up to get started",
                font=("Segoe UI", 11), bg="#1a1a2e", fg="#888").pack(pady=(0, 30))

        tk.Label(self.container, text="Username", font=("Segoe UI", 10),
                bg="#1a1a2e", fg="#fff", anchor="w").pack(fill="x", padx=50, pady=(10, 5))
        
        self.username = tk.Entry(self.container, font=("Segoe UI", 13),
                                bg="#16213e", fg="white", insertbackground="#00d4ff",
                                bd=0, relief=tk.FLAT)
        self.username.pack(ipady=12, fill="x", padx=50, pady=5)

        tk.Label(self.container, text="Password", font=("Segoe UI", 10),
                bg="#1a1a2e", fg="#fff", anchor="w").pack(fill="x", padx=50, pady=(15, 5))
        
        self.password = tk.Entry(self.container, font=("Segoe UI", 13),
                                bg="#16213e", fg="white", insertbackground="#00d4ff",
                                bd=0, show="●", relief=tk.FLAT)
        self.password.pack(ipady=12, fill="x", padx=50, pady=5)

        signup_btn = tk.Button(self.container, text="SIGN UP", command=self.signup,
                            bg="#4CAF50", fg="#fff", font=("Segoe UI", 13, "bold"),
                            bd=0, cursor="hand2", relief=tk.FLAT)
        signup_btn.pack(fill="x", padx=50, pady=(30, 10), ipady=12)

        tk.Button(self.container, text="← Back to login", command=self.show_login,
                bg="#1a1a2e", fg="#00d4ff", font=("Segoe UI", 11),
                bd=0, cursor="hand2", relief=tk.FLAT).pack(pady=10)

    def signup(self):
        """Process signup"""
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "All fields required")
            return
        if self.db.signup(user, pwd):
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login()
        else:
            messagebox.showerror("Error", "Username already exists")

    def login(self):
        """Process login"""
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if self.db.login(user, pwd):
            self.container.destroy()
            self.marquee_label.destroy()
            app = ShopApp(self.root)
        else:
            messagebox.showerror("Error", "Invalid username or password")
