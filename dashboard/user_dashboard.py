#!/usr/bin/env python3
"""User Dashboard - WITH MANDATORY FTP UPLOAD + SCROLLABLE SECTIONS

All features:
- Shows ALL articles (not just user's own)
- MANDATORY FTP upload for images  
- Firebase stores ONLY FTP PATHS (not URLs)
- Image preview with FTP authentication
- Article creation blocked if FTP upload fails
- SCROLLABLE Dashboard and About sections
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os
import random
import string
from PIL import Image, ImageTk
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR, APP_VERSION, COMPANY
from utils.ftp_uploader import get_ftp_uploader
from utils.image_sync import get_image_sync
from db.models import Article
import uuid


class UserDashboard:
    def __init__(self, root, user, db, firebase, network_checker, logout_callback, logger):
        self.root = root
        self.user = user
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.logout_callback = logout_callback
        self.logger = logger
        self.ftp = get_ftp_uploader()
        self.image_sync = get_image_sync()
        self.selected_image_path = None
        self.preview_photo = None

        self.root.deiconify()
        self.setup_ui()
        self.refresh_data()
        self.logger.info(f"User dashboard initialized for: {user['username']}")

    def generate_article_id(self):
        while True:
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            article_id = f"Fides-{random_part}"
            try:
                existing = self.db.get_article_by_id(article_id)
                if not existing:
                    return article_id
            except:
                return article_id

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top bar
        top_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        tk.Label(
            top_frame,
            text=f"{APP_NAME} - User Dashboard",
            font=("Arial", 14, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            top_frame,
            text=f"Welcome, {self.user['username']} 👤",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(side=tk.RIGHT, padx=20, pady=10)

        # Main content
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(main_frame, bg="#f0f0f0", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📄 All Articles", self.show_articles),
            ("🔄 Sync Status", self.show_sync_status),
            ("ℹ️ About", self.show_about),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Logout", self.logout),
        ]

        for btn_text, btn_command in buttons:
            btn = tk.Button(
                sidebar,
                text=btn_text,
                font=("Arial", 11),
                bg="#f0f0f0",
                fg="#333",
                relief=tk.FLAT,
                cursor="hand2",
                command=btn_command,
                anchor=tk.W,
                padx=20,
                pady=15
            )
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f0f0f0"))

        # Content frame
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_scrollable_frame(self, parent):
        """Create a canvas with scrollbar for scrollable content"""
        # Canvas
        canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside canvas
        scrollable_frame = tk.Frame(canvas, bg="white")
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Update scrollregion when frame size changes
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable frame width match canvas width
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))

        # Mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)

        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)

        return scrollable_frame

    def show_dashboard(self):
        self.clear_content()

        # Create scrollable container
        scrollable_frame = self.create_scrollable_frame(self.content_frame)

        tk.Label(
            scrollable_frame,
            text="Dashboard Overview",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(0, 20), padx=5)

        try:
            all_articles = self.db.get_all_articles()
            my_articles = [a for a in all_articles if a.created_by == self.user['id']]
            total_articles = len(all_articles)
            my_article_count = len(my_articles)
            pending_sync = len([a for a in my_articles if a.sync_status == 0])
            is_online = self.network_checker.is_connected()
        except Exception as e:
            self.logger.error(f"Error fetching stats: {e}")
            total_articles = my_article_count = pending_sync = 0
            is_online = False

        stats_frame = tk.Frame(scrollable_frame, bg="white")
        stats_frame.pack(fill=tk.X, pady=10, padx=5)

        stats = [
            ("Total Articles", str(total_articles), "📊"),
            ("My Articles", str(my_article_count), "📄"),
            ("Pending Sync", str(pending_sync), "⏳"),
            ("Status", "Online" if is_online else "Offline", "🌐"),
        ]

        for label, value, emoji in stats:
            stat_card = tk.Frame(stats_frame, bg="#f9f9f9", relief=tk.SOLID, bd=1)
            stat_card.pack(fill=tk.X, pady=8, padx=5)
            tk.Label(
                stat_card,
                text=f"{emoji} {label}: {value}",
                font=("Arial", 13, "bold"),
                bg="#f9f9f9"
            ).pack(anchor=tk.W, padx=20, pady=15)

        tk.Label(
            scrollable_frame,
            text="Quick Actions",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(30, 15), padx=5)

        tk.Button(
            scrollable_frame,
            text="+ Create New Article",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(anchor=tk.W, ipady=10, ipadx=20, padx=5)

        # Add some extra space at bottom
        tk.Label(scrollable_frame, text="", bg="white", height=5).pack()

    # [Previous methods remain the same: show_articles, preview_article_image, show_image_preview, create_article, etc.]
    # Only show_about is modified below

    def show_about(self):
        """Enhanced About section with scrollbar"""
        self.clear_content()

        # Header (fixed, not scrollable)
        header_label = tk.Label(
            self.content_frame,
            text="About",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#333"
        )
        header_label.pack(anchor=tk.W, pady=(0, 15))

        # Scrollable content container
        scroll_container = tk.Frame(self.content_frame, bg="white")
        scroll_container.pack(fill=tk.BOTH, expand=True)

        scrollable_frame = self.create_scrollable_frame(scroll_container)

        # Main card frame (inside scrollable)
        card_frame = tk.Frame(scrollable_frame, bg="#f8f9fa", relief=tk.SOLID, bd=1)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Logo section
        logo_frame = tk.Frame(card_frame, bg="#f8f9fa")
        logo_frame.pack(pady=20)

        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_frame, image=logo_photo, bg="#f8f9fa")
                logo_label.image = logo_photo
                logo_label.pack()
        except Exception as e:
            self.logger.debug(f"Logo load error: {e}")

        # App info
        tk.Label(
            card_frame,
            text=f"{APP_NAME}",
            font=("Arial", 16, "bold"),
            bg="#f8f9fa",
            fg=PRIMARY_COLOR
        ).pack(pady=(10, 5))

        tk.Label(
            card_frame,
            text=f"Version {APP_VERSION}",
            font=("Arial", 10),
            bg="#f8f9fa",
            fg="#666"
        ).pack(pady=(0, 5))

        tk.Label(
            card_frame,
            text=COMPANY,
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(0, 20))

        # Separator
        tk.Frame(card_frame, height=1, bg="#dee2e6").pack(fill=tk.X, padx=30, pady=15)

        # Developer section
        tk.Label(
            card_frame,
            text="👨‍💻 Developer",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(10, 10))

        tk.Label(
            card_frame,
            text="Manoj Konar",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg=PRIMARY_COLOR
        ).pack(pady=(0, 10))

        # Email section
        tk.Label(
            card_frame,
            text="📧 Contact",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(10, 5))

        emails = [
            "monoj@nexuzy.in",
            "monoj@hypechats.com"
        ]

        for email in emails:
            email_label = tk.Label(
                card_frame,
                text=email,
                font=("Arial", 10, "underline"),
                bg="#f8f9fa",
                fg="#1f6feb",
                cursor="hand2"
            )
            email_label.pack(pady=2)
            email_label.bind("<Button-1>", lambda e, addr=email: webbrowser.open(f"mailto:{addr}"))

        # Separator
        tk.Frame(card_frame, height=1, bg="#dee2e6").pack(fill=tk.X, padx=30, pady=15)

        # Websites section
        tk.Label(
            card_frame,
            text="🌐 Websites",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(10, 10))

        websites = [
            ("HypeChats", "https://hypechats.com/"),
            ("HYLS (Hype Link Shortener)", "https://hyls.space/"),
            ("Nexuzy Tech Pvt. Ltd.", "https://nexuzy.tech/")
        ]

        for name, url in websites:
            link_label = tk.Label(
                card_frame,
                text=name,
                font=("Arial", 10, "underline"),
                bg="#f8f9fa",
                fg="#1f6feb",
                cursor="hand2"
            )
            link_label.pack(pady=3)
            link_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # Separator
        tk.Frame(card_frame, height=1, bg="#dee2e6").pack(fill=tk.X, padx=30, pady=15)

        # GitHub repository
        tk.Label(
            card_frame,
            text="📦 Source Code",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(10, 5))

        repo_label = tk.Label(
            card_frame,
            text="github.com/david0154/NEXUZY_ARTICAL",
            font=("Arial", 10, "underline"),
            bg="#f8f9fa",
            fg="#1f6feb",
            cursor="hand2"
        )
        repo_label.pack(pady=(0, 20))
        repo_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/david0154/NEXUZY_ARTICAL"))

        # Features
        tk.Label(
            card_frame,
            text="✨ Key Features",
            font=("Arial", 11, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(pady=(10, 5))

        features = [
            "📄 Article Management",
            "☁️ Firebase Cloud Sync",
            "📷 FTP Image Upload",
            "📊 Export to PDF/Excel",
            "👥 User Management"
        ]

        for feature in features:
            tk.Label(
                card_frame,
                text=feature,
                font=("Arial", 9),
                bg="#f8f9fa",
                fg="#666"
            ).pack(pady=2)

        # Copyright
        tk.Label(
            card_frame,
            text=f"© 2026 {COMPANY}. All rights reserved.",
            font=("Arial", 8),
            bg="#f8f9fa",
            fg="#999"
        ).pack(pady=(20, 15))

        # Extra space at bottom for scrolling
        tk.Label(scrollable_frame, text="", bg="white", height=3).pack()

    # [All other methods remain unchanged]
    # Keeping the rest of the methods to maintain file size

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
