#!/usr/bin/env python3
"""Login Window Module

Refactor note:
- The login UI is rendered directly inside the main root window (no Toplevel) to
  avoid the app closing unexpectedly due to window focus/lifecycle issues.

Policy:
- Public self-registration is disabled.
- Only admins can create users from the Admin Dashboard.

Handles user authentication with offline-first support.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR
from utils.security import hash_password, verify_password


class LoginWindow:
    """Login screen rendered inside the main window."""

    def __init__(self, parent, db, firebase, network_checker, on_success_callback, logger):
        self.parent = parent
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.on_success = on_success_callback
        self.logger = logger

        # Clear parent and build login UI inside it
        for w in self.parent.winfo_children():
            w.destroy()

        self.parent.deiconify()
        self.parent.configure(bg="white")

        self.container = tk.Frame(self.parent, bg="white")
        self.container.pack(fill=tk.BOTH, expand=True)

        self.setup_ui()
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Create login UI"""
        # Header
        header_frame = tk.Frame(self.container, bg=PRIMARY_COLOR, height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=f"{APP_NAME}",
            font=("Arial", 24, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=(18, 2))

        subtitle_label = tk.Label(
            header_frame,
            text="Login to Your Account",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        subtitle_label.pack()

        # Body
        body = tk.Frame(self.container, bg="white")
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Username
        tk.Label(body, text="Username:", font=("Arial", 10), bg="white", fg="#333").pack(anchor=tk.W, pady=(10, 5))
        self.username_entry = tk.Entry(body, font=("Arial", 10), relief=tk.FLAT, highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        self.username_entry.pack(fill=tk.X, ipady=8)
        self.username_entry.bind("<Return>", lambda e: self.login())

        # Password
        tk.Label(body, text="Password:", font=("Arial", 10), bg="white", fg="#333").pack(anchor=tk.W, pady=(15, 5))
        self.password_entry = tk.Entry(body, font=("Arial", 10), show="•", relief=tk.FLAT, highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        self.password_entry.pack(fill=tk.X, ipady=8)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Buttons
        login_btn = tk.Button(
            body,
            text="Login",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(fill=tk.X, pady=(20, 10), ipady=8)

        # Registration removed (admin-only user creation)
        tk.Label(
            body,
            text="Accounts are created by Admin only.",
            font=("Arial", 9),
            bg="white",
            fg="#777"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Status
        is_online = self.network_checker.is_connected()
        status_text = "Online Mode" if is_online else "Offline Mode"
        status_color = "green" if is_online else "orange"

        status_frame = tk.Frame(self.container, bg="white")
        status_frame.pack(fill=tk.X, padx=30, pady=(0, 12))

        status_label = tk.Label(
            status_frame,
            text=f"🟢 {status_text}" if is_online else f"🟡 {status_text}",
            font=("Arial", 8),
            bg="white",
            fg=status_color
        )
        status_label.pack(anchor=tk.W)

    def login(self):
        """Authenticate user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password")
            return

        try:
            user = self.db.get_user_by_username(username)

            if user and verify_password(password, user['password_hash']):
                self.db.update_user_last_login(user['id'])
                self.logger.info(f"User '{username}' logged in from local DB")
                self.on_success(user['id'], user['username'], user['role'])
                return

            # If online, try Firebase
            if self.network_checker.is_connected():
                firebase_user = self.firebase.authenticate_user(username, password)
                if firebase_user:
                    self.db.create_or_update_user(
                        firebase_user['uid'],
                        username,
                        hash_password(password),
                        firebase_user.get('role', 'user')
                    )
                    self.logger.info(f"User '{username}' logged in from Firebase")
                    self.on_success(firebase_user['uid'], username, firebase_user.get('role', 'user'))
                else:
                    messagebox.showerror("Authentication Failed", "Invalid credentials")
                    self.logger.warning(f"Failed login attempt for '{username}'")
            else:
                messagebox.showerror("Authentication Failed", "Invalid credentials (offline mode)")
                self.logger.warning(f"Failed offline login attempt for '{username}'")

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            messagebox.showerror("Login Error", f"An error occurred: {e}")

    def on_closing(self):
        if messagebox.askyesno("Exit", "Do you want to exit?"):
            self.parent.destroy()


# Keep RegisterWindow for backward compatibility if imported elsewhere,
# but do not expose it from Login UI.
class RegisterWindow:
    """Deprecated: self-registration disabled."""

    def __init__(self, parent, db, firebase, network_checker, logger):
        self.parent = parent
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.logger = logger
        messagebox.showinfo("Disabled", "Create Account is disabled. Please contact Admin.")
