#!/usr/bin/env python3
"""
NEXUZY ARTICAL - Main Application Entry Point
Version: 1.0.0
Developer: Manoj Konar
Email: monoj@nexuzy.in
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    PRIMARY_COLOR, DEVELOPER_NAME, DEVELOPER_EMAIL
)
from utils.logger import Logger
from utils.network import NetworkChecker
from utils.security import hash_password
from db.local_db import LocalDatabase
from db.firebase_sync import FirebaseSync
from auth.login import LoginWindow


class NexuzyApp:
    """Main application controller"""

    def __init__(self, root):
        self.root = root
        self.user = None
        self.logger = Logger(__name__)
        self.network_checker = NetworkChecker()
        self.db = LocalDatabase()
        self.firebase = FirebaseSync()
        self.current_user = None

        self.setup_window()
        self.initialize_app()
        self.show_login()

    def setup_window(self):
        """Configure main window"""
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#f0f0f0")

        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logger.info(f"{APP_NAME} v{APP_VERSION} window initialized")

    def ensure_default_admin(self):
        """Create default admin account once (if not exists)."""
        try:
            default_username = "david"
            default_password = "784577"
            default_role = "admin"

            existing = self.db.get_user_by_username(default_username)
            if existing:
                return

            import uuid
            user_id = str(uuid.uuid4())
            self.db.create_or_update_user(user_id, default_username, hash_password(default_password), default_role)
            self.logger.info("Default admin created: david / 784577")

            # If online + firebase is initialized, try to create there as well
            try:
                if self.network_checker.is_connected() and getattr(self.firebase, "initialized", False):
                    self.firebase.create_user(user_id, default_username, default_password, default_role)
            except Exception as e:
                self.logger.warning(f"Default admin Firebase sync skipped: {e}")

        except Exception as e:
            self.logger.warning(f"Failed to ensure default admin: {e}")

    def initialize_app(self):
        """Initialize application components"""
        try:
            # Initialize local database
            self.db.initialize()
            self.logger.info("Local database initialized")

            # Check internet connectivity
            is_online = self.network_checker.is_connected()
            self.logger.info(f"Network status: {'Online' if is_online else 'Offline'}")

            # Initialize Firebase if online
            if is_online:
                try:
                    self.firebase.initialize()
                    self.logger.info("Firebase initialized")
                except Exception as e:
                    self.logger.warning(f"Firebase initialization failed: {e}")

            # Create default admin after DB init
            self.ensure_default_admin()

        except Exception as e:
            self.logger.error(f"App initialization failed: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")
            self.root.destroy()

    def show_login(self):
        """Display login window (rendered inside root)"""
        try:
            self.logger.info("Showing login window")
            LoginWindow(
                self.root,
                self.db,
                self.firebase,
                self.network_checker,
                self.on_login_success,
                self.logger
            )
        except Exception as e:
            self.logger.error(f"Login window error: {e}")
            messagebox.showerror("Error", f"Failed to show login: {e}")
            self.root.destroy()

    def on_login_success(self, user_id, username, role):
        """Handle successful login"""
        self.current_user = {
            'id': user_id,
            'username': username,
            'role': role,
            'login_time': datetime.now()
        }
        self.logger.info(f"User '{username}' ({role}) logged in successfully")

        # Import dashboard based on role
        if role == 'admin':
            from dashboard.admin_dashboard import AdminDashboard
            dashboard_class = AdminDashboard
        else:
            from dashboard.user_dashboard import UserDashboard
            dashboard_class = UserDashboard

        try:
            self.root.deiconify()
            dashboard_class(
                self.root,
                self.current_user,
                self.db,
                self.firebase,
                self.network_checker,
                self.on_logout,
                self.logger
            )
        except Exception as e:
            self.logger.error(f"Dashboard initialization failed: {e}")
            messagebox.showerror("Error", f"Failed to load dashboard: {e}")

    def on_logout(self):
        """Handle logout"""
        if self.current_user:
            self.logger.info(f"User '{self.current_user['username']}' logged out")
        self.current_user = None
        self.show_login()

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", f"Do you want to exit {APP_NAME}?"):
            self.logger.info(f"{APP_NAME} closed by user")
            try:
                self.db.close()
            except Exception:
                pass
            self.root.destroy()


def main():
    """Application entry point"""
    try:
        root = tk.Tk()
        NexuzyApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
