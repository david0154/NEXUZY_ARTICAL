#!/usr/bin/env python3
"""Login Window Module - FIXED SIZING"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR
from utils.security import verify_password


class LoginWindow:
    """Login window with proper sizing"""

    def __init__(self, root, db, firebase, network_checker, on_success, logger):
        self.root = root
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.on_success = on_success
        self.logger = logger

        # Hide main window
        self.root.withdraw()

        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title(f"{APP_NAME} - Login")
        
        # FIXED: Proper window size
        window_width = 450
        window_height = 500
        
        # Center on screen
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg="white")

        # Icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.login_window.iconbitmap(icon_path)
        except:
            pass

        # Protocol
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_ui()
        self.logger.info("Login window opened")

    def setup_ui(self):
        """Create login UI"""
        # Header
        header_frame = tk.Frame(self.login_window, bg=PRIMARY_COLOR, height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=APP_NAME,
            font=("Arial", 20, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(pady=(30, 5))

        tk.Label(
            header_frame,
            text="Login to your account",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack()

        # Form container
        form_frame = tk.Frame(self.login_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Username
        tk.Label(
            form_frame,
            text="Username",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(0, 5))

        self.username_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            relief=tk.SOLID,
            bd=1
        )
        self.username_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))
        self.username_entry.focus()

        # Password
        tk.Label(
            form_frame,
            text="Password",
            font=("Arial", 10, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            show="•",
            relief=tk.SOLID,
            bd=1
        )
        self.password_entry.pack(fill=tk.X, ipady=8, pady=(0, 30))

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Login button
        login_btn = tk.Button(
            form_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(fill=tk.X, ipady=12)

        # Footer
        footer_frame = tk.Frame(self.login_window, bg="#f5f5f5", height=60)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)

        status = "🌐 Online" if self.network_checker.is_connected() else "📴 Offline"
        tk.Label(
            footer_frame,
            text=status,
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#666"
        ).pack(pady=20)

    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter username and password")
            return

        try:
            user = self.db.get_user_by_username(username)

            if not user:
                messagebox.showerror("Login Error", "Invalid username or password")
                self.logger.warning(f"Failed login attempt: {username}")
                return

            if not verify_password(password, user['password_hash']):
                messagebox.showerror("Login Error", "Invalid username or password")
                self.logger.warning(f"Failed login attempt: {username}")
                return

            # Update last login
            self.db.update_user_last_login(user['id'])

            self.logger.info(f"Successful login: {username} ({user['role']})")
            self.login_window.destroy()
            self.on_success(user['id'], username, user['role'])

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            messagebox.showerror("Login Error", f"An error occurred: {e}")

    def on_close(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.logger.info("Login window closed by user")
            self.root.destroy()
