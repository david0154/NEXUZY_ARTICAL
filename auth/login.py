#!/usr/bin/env python3
"""
Login Window Module
Handles user authentication with offline-first support
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from utils.security import hash_password, verify_password


class LoginWindow:
    """Login window with support for offline and online modes"""

    def __init__(self, parent, db, firebase, network_checker, on_success_callback, logger):
        self.parent = parent
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.on_success = on_success_callback
        self.logger = logger
        
        self.login_window = tk.Toplevel(parent)
        self.login_window.title(f"{APP_NAME} - Login")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg="white")
        
        # Center on parent
        self.login_window.transient(parent)
        self.login_window.grab_set()
        
        self.setup_ui()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Create login UI"""
        # Header
        header_frame = tk.Frame(self.login_window, bg=PRIMARY_COLOR, height=80)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text=f"{APP_NAME}",
            font=("Arial", 24, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Login to Your Account",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        subtitle_label.pack()
        
        # Form frame
        form_frame = tk.Frame(self.login_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Username
        tk.Label(
            form_frame,
            text="Username:",
            font=("Arial", 10),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=("Arial", 10),
            width=30,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=PRIMARY_COLOR
        )
        self.username_entry.pack(fill=tk.X, ipady=8)
        self.username_entry.bind("<Return>", lambda e: self.login())
        
        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 10),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(15, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 10),
            width=30,
            show="•",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=PRIMARY_COLOR
        )
        self.password_entry.pack(fill=tk.X, ipady=8)
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Login button
        login_btn = tk.Button(
            form_frame,
            text="Login",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(fill=tk.X, pady=(20, 10), ipady=8)
        
        # Register button
        register_btn = tk.Button(
            form_frame,
            text="Create New Account",
            font=("Arial", 10),
            bg="white",
            fg=PRIMARY_COLOR,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_register
        )
        register_btn.pack(fill=tk.X, pady=(0, 10), ipady=8)
        
        # Status bar
        is_online = self.network_checker.is_connected()
        status_text = "Online Mode" if is_online else "Offline Mode"
        status_color = "green" if is_online else "orange"
        
        status_frame = tk.Frame(self.login_window, bg="white")
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
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
            # Try to authenticate from local database first
            user = self.db.get_user_by_username(username)
            
            if user and verify_password(password, user['password_hash']):
                # Update last login
                self.db.update_user_last_login(user['id'])
                self.logger.info(f"User '{username}' logged in from local DB")
                
                # Close login window
                self.login_window.destroy()
                
                # Call success callback
                self.on_success(user['id'], user['username'], user['role'])
            else:
                # If online, try Firebase
                if self.network_checker.is_connected():
                    firebase_user = self.firebase.authenticate_user(username, password)
                    if firebase_user:
                        # Sync to local DB
                        self.db.create_or_update_user(
                            firebase_user['uid'],
                            username,
                            hash_password(password),
                            firebase_user.get('role', 'user')
                        )
                        self.logger.info(f"User '{username}' logged in from Firebase")
                        
                        self.login_window.destroy()
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

    def show_register(self):
        """Show registration window"""
        RegisterWindow(
            self.login_window,
            self.db,
            self.firebase,
            self.network_checker,
            self.logger
        )

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit", "Do you want to exit?"):
            self.login_window.destroy()
            self.parent.destroy()


class RegisterWindow:
    """Registration window for new users"""

    def __init__(self, parent, db, firebase, network_checker, logger):
        self.parent = parent
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.logger = logger
        
        self.register_window = tk.Toplevel(parent)
        self.register_window.title(f"{APP_NAME} - Register")
        self.register_window.geometry("400x400")
        self.register_window.resizable(False, False)
        self.register_window.configure(bg="white")
        
        self.register_window.transient(parent)
        self.register_window.grab_set()
        
        self.setup_ui()

    def setup_ui(self):
        """Create registration UI"""
        # Header
        header_frame = tk.Frame(self.register_window, bg=PRIMARY_COLOR, height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Create Account",
            font=("Arial", 18, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(pady=12)
        
        # Form frame
        form_frame = tk.Frame(self.register_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Username
        tk.Label(form_frame, text="Username:", font=("Arial", 10), bg="white").pack(anchor=tk.W, pady=(5, 3))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, relief=tk.FLAT, bd=0, highlightthickness=1)
        self.username_entry.pack(fill=tk.X, ipady=7)
        
        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 10), bg="white").pack(anchor=tk.W, pady=(15, 3))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show="•", relief=tk.FLAT, bd=0, highlightthickness=1)
        self.password_entry.pack(fill=tk.X, ipady=7)
        
        # Confirm Password
        tk.Label(form_frame, text="Confirm Password:", font=("Arial", 10), bg="white").pack(anchor=tk.W, pady=(15, 3))
        self.confirm_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, show="•", relief=tk.FLAT, bd=0, highlightthickness=1)
        self.confirm_entry.pack(fill=tk.X, ipady=7)
        
        # Role selection
        tk.Label(form_frame, text="Role:", font=("Arial", 10), bg="white").pack(anchor=tk.W, pady=(15, 3))
        self.role_var = tk.StringVar(value="user")
        role_frame = tk.Frame(form_frame, bg="white")
        role_frame.pack(anchor=tk.W)
        tk.Radiobutton(role_frame, text="User", variable=self.role_var, value="user", bg="white").pack(side=tk.LEFT)
        tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="admin", bg="white").pack(side=tk.LEFT, padx=20)
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            btn_frame,
            text="Register",
            font=("Arial", 10, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.register
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=7)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 10),
            bg="#e0e0e0",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.register_window.destroy
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7)

    def register(self):
        """Register new user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_var.get()
        
        if not all([username, password, confirm]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Password Error", "Password must be at least 6 characters")
            return
        
        if password != confirm:
            messagebox.showwarning("Password Error", "Passwords do not match")
            return
        
        try:
            # Check if user exists
            existing = self.db.get_user_by_username(username)
            if existing:
                messagebox.showerror("Registration Error", "Username already exists")
                return
            
            # Create new user in local DB
            import uuid
            user_id = str(uuid.uuid4())
            password_hash = hash_password(password)
            
            self.db.create_or_update_user(user_id, username, password_hash, role)
            
            # Try to sync to Firebase if online
            if self.network_checker.is_connected():
                self.firebase.create_user(user_id, username, password, role)
                self.logger.info(f"User '{username}' registered and synced to Firebase")
            else:
                self.logger.info(f"User '{username}' registered locally (will sync when online)")
            
            messagebox.showinfo("Success", "Account created successfully!")
            self.register_window.destroy()
            
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            messagebox.showerror("Registration Error", f"Failed to create account: {e}")
