#!/usr/bin/env python3
"""Login Window Module - WITH LOGO AND REMEMBER ME"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import json
from PIL import Image, ImageTk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR
from utils.security import verify_password


class LoginWindow:
    """Login window with logo, remember me, and saved credentials"""

    def __init__(self, root, db, firebase, network_checker, on_success, logger):
        self.root = root
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.on_success = on_success
        self.logger = logger
        self.credentials_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")

        # Hide main window
        self.root.withdraw()

        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title(f"{APP_NAME} - Login")
        
        # FIXED: Proper window size with space for logo
        window_width = 450
        window_height = 600
        
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
        self.load_saved_credentials()
        self.logger.info("Login window opened")

    def setup_ui(self):
        """Create login UI with logo and remember me"""
        # Header with logo
        header_frame = tk.Frame(self.login_window, bg=PRIMARY_COLOR, height=180)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Try to load logo
        logo_loaded = False
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = tk.Label(
                    header_frame,
                    image=self.logo_photo,
                    bg=PRIMARY_COLOR
                )
                logo_label.pack(pady=(20, 10))
                logo_loaded = True
            except Exception as e:
                self.logger.debug(f"Could not load logo: {e}")
        
        # If logo not loaded, show app initial
        if not logo_loaded:
            tk.Label(
                header_frame,
                text=APP_NAME[0],
                font=("Arial", 48, "bold"),
                bg=PRIMARY_COLOR,
                fg="white"
            ).pack(pady=(20, 10))

        tk.Label(
            header_frame,
            text=APP_NAME,
            font=("Arial", 18, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(pady=(0, 5))

        tk.Label(
            header_frame,
            text="Login to your account",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack()

        # Form container
        form_frame = tk.Frame(self.login_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

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
        self.username_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
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
        self.password_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))

        # Remember Me checkbox
        self.remember_var = tk.BooleanVar(value=False)
        remember_frame = tk.Frame(form_frame, bg="white")
        remember_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Checkbutton(
            remember_frame,
            text="Remember me",
            font=("Arial", 9),
            bg="white",
            variable=self.remember_var,
            cursor="hand2"
        ).pack(side=tk.LEFT)

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

    def load_saved_credentials(self):
        """Load saved credentials if remember me was checked"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    if data.get('remember'):
                        self.username_entry.insert(0, data.get('username', ''))
                        self.password_entry.insert(0, data.get('password', ''))
                        self.remember_var.set(True)
        except Exception as e:
            self.logger.debug(f"Could not load credentials: {e}")

    def save_credentials(self, username, password, remember):
        """Save credentials if remember me is checked"""
        try:
            data = {
                'remember': remember,
                'username': username if remember else '',
                'password': password if remember else ''
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.debug(f"Could not save credentials: {e}")

    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        remember = self.remember_var.get()

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

            # Save credentials if remember me is checked
            self.save_credentials(username, password, remember)

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
