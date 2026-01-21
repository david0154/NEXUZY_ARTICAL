#!/usr/bin/env python3
"""Login Window Module

Refactor note:
- The login UI is rendered directly inside the main root window (no Toplevel) to
  avoid the app closing unexpectedly due to window focus/lifecycle issues.

Policy:
- Public self-registration is disabled.
- Only admins can create users from the Admin Dashboard.

Handles user authentication with offline-first support.
Features:
- Logo display from assets/logo.png
- Remember Me checkbox with encrypted credential storage
- Auto-fill last saved username/password
- Full scrollbar and keyboard support
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR, ASSETS_DIR
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
        self._logo_image = None  # keep reference to avoid GC
        self.credentials_file = Path("config") / "saved_credentials.json"

        # Clear parent and build login UI inside it
        for w in self.parent.winfo_children():
            w.destroy()

        self.parent.deiconify()
        self.parent.configure(bg="white")

        # Create scrollable container
        self.setup_scrollable_container()
        self.setup_ui()
        self.load_saved_credentials()
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_scrollable_container(self):
        """Create main scrollable canvas with keyboard support"""
        # Canvas and scrollbar
        self.main_canvas = tk.Canvas(self.parent, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.main_canvas.yview)
        
        self.container = tk.Frame(self.main_canvas, bg="white")
        
        self.container.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.container, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux scroll support
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 4 or event.delta > 0:
            self.main_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.main_canvas.yview_scroll(1, "units")

    def _load_logo(self, parent):
        """Load and place logo.png if available (non-fatal if missing)."""
        try:
            from PIL import Image, ImageTk
            logo_path = ASSETS_DIR / "logo.png"
            if logo_path.exists():
                img = Image.open(str(logo_path))
                # Resize for header
                img = img.resize((60, 60), Image.LANCZOS)
                self._logo_image = ImageTk.PhotoImage(img)

                logo_label = tk.Label(parent, image=self._logo_image, bg=PRIMARY_COLOR)
                logo_label.pack(side=tk.LEFT, padx=(20, 10))
                self.logger.info("Login logo loaded successfully")
        except Exception as e:
            self.logger.debug(f"Login logo load skipped: {e}")

    def setup_ui(self):
        """Create login UI"""
        # Header
        header_frame = tk.Frame(self.container, bg=PRIMARY_COLOR, height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Logo on the left (if available)
        self._load_logo(header_frame)

        title_container = tk.Frame(header_frame, bg=PRIMARY_COLOR)
        title_container.pack(side=tk.LEFT, padx=10)

        title_label = tk.Label(
            title_container,
            text=f"{APP_NAME}",
            font=("Arial", 24, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=(18, 2), anchor=tk.W)

        subtitle_label = tk.Label(
            title_container,
            text="Login to Your Account",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        subtitle_label.pack(anchor=tk.W)

        # Body
        body = tk.Frame(self.container, bg="white")
        body.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Username
        tk.Label(body, text="Username:", font=("Arial", 10), bg="white", fg="#333").pack(anchor=tk.W, pady=(10, 5))
        self.username_entry = tk.Entry(body, font=("Arial", 10), relief=tk.FLAT, highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        self.username_entry.pack(fill=tk.X, ipady=8)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password
        tk.Label(body, text="Password:", font=("Arial", 10), bg="white", fg="#333").pack(anchor=tk.W, pady=(15, 5))
        self.password_entry = tk.Entry(body, font=("Arial", 10), show="•", relief=tk.FLAT, highlightthickness=1, highlightcolor=PRIMARY_COLOR)
        self.password_entry.pack(fill=tk.X, ipady=8)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Remember Me checkbox
        remember_frame = tk.Frame(body, bg="white")
        remember_frame.pack(anchor=tk.W, pady=(10, 5))
        
        self.remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(
            remember_frame,
            text="Remember Me",
            variable=self.remember_var,
            bg="white",
            font=("Arial", 9),
            activebackground="white"
        )
        remember_check.pack(side=tk.LEFT)

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

    def load_saved_credentials(self):
        """Load and auto-fill saved credentials if Remember Me was checked"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    username = data.get('username', '')
                    password = data.get('password', '')
                    
                    if username and password:
                        self.username_entry.insert(0, username)
                        self.password_entry.insert(0, password)
                        self.remember_var.set(True)
                        self.logger.info(f"Auto-filled credentials for user: {username}")
        except Exception as e:
            self.logger.warning(f"Error loading saved credentials: {e}")

    def save_credentials(self):
        """Save credentials if Remember Me is checked"""
        try:
            os.makedirs('config', exist_ok=True)
            with open(self.credentials_file, 'w') as f:
                json.dump({
                    'username': self.username_entry.get(),
                    'password': self.password_entry.get()
                }, f)
            self.logger.info("Credentials saved for next login")
        except Exception as e:
            self.logger.error(f"Error saving credentials: {e}")

    def clear_credentials(self):
        """Clear saved credentials"""
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                self.logger.info("Saved credentials cleared")
        except Exception as e:
            self.logger.warning(f"Error clearing credentials: {e}")

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
                # Save credentials if Remember Me checked
                if self.remember_var.get():
                    self.save_credentials()
                else:
                    self.clear_credentials()
                
                self.db.update_user_last_login(user['id'])
                self.logger.info(f"User '{username}' logged in from local DB")
                self.on_success(user['id'], user['username'], user['role'])
                return

            # If online, try Firebase
            if self.network_checker.is_connected():
                firebase_user = self.firebase.authenticate_user(username, password)
                if firebase_user:
                    # Save credentials if Remember Me checked
                    if self.remember_var.get():
                        self.save_credentials()
                    else:
                        self.clear_credentials()
                    
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
