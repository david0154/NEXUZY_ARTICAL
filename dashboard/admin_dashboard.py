#!/usr/bin/env python3
"""Admin Dashboard Module - FIXED WINDOW SIZING

Full control panel for administrators

Features:
- Fixed window sizing (content fills entire space)
- Fixed dialog closing bug
- FTP image upload with progress
- Image URL storage in Firebase
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR
from utils.export import ExportManager
from utils.ftp_uploader import get_ftp_uploader


class AdminDashboard:
    """Admin dashboard with full application control"""

    def __init__(self, root, user, db, firebase, network_checker, logout_callback, logger):
        self.root = root
        self.user = user
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.logout_callback = logout_callback
        self.logger = logger
        self.exporter = ExportManager()
        self.ftp = get_ftp_uploader()
        self.selected_image_path = None

        self.root.deiconify()
        self.setup_ui()
        self.refresh_data()
        self.logger.info(f"Admin dashboard initialized for user: {user['username']}")

    def generate_article_id(self):
        """Generate unique Fides-XXXXXX article ID"""
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
        """Create admin dashboard UI - FIXED SIZING"""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top bar with username
        top_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        title_label = tk.Label(
            top_frame,
            text=f"{APP_NAME} - Admin Dashboard",
            font=("Arial", 14, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        user_info = tk.Label(
            top_frame,
            text=f"Welcome, {self.user['username']} ({self.user['role'].upper()}) 👤",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        user_info.pack(side=tk.RIGHT, padx=20, pady=10)

        # Main content frame
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar - FIXED WIDTH
        sidebar = tk.Frame(main_frame, bg="#f0f0f0", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📄 Articles", self.show_articles),
            ("👥 Users", self.show_users),
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

        # CRITICAL FIX: Content frame directly in main_frame (no canvas wrapper)
        # This makes content use 100% of available space
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_dashboard()

    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show main dashboard"""
        self.clear_content()

        title = tk.Label(
            self.content_frame,
            text="Dashboard Overview",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        )
        title.pack(anchor=tk.W, pady=(0, 20))

        try:
            total_users = len(self.db.get_all_users())
            total_articles = self.db.get_articles_count()
            pending_sync = self.db.get_pending_articles_count()
            is_online = self.network_checker.is_connected()
        except Exception as e:
            self.logger.error(f"Error fetching dashboard stats: {e}")
            total_users = total_articles = pending_sync = 0
            is_online = False

        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)

        stats = [
            ("Total Users", str(total_users), "👥"),
            ("Total Articles", str(total_articles), "📄"),
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
            self.content_frame,
            text="Quick Actions",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(30, 15))

        actions_frame = tk.Frame(self.content_frame, bg="white")
        actions_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            actions_frame,
            text="+ Create New Article",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(side=tk.LEFT, padx=5, ipady=10, ipadx=20)

        tk.Button(
            actions_frame,
            text="+ Add User",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_user
        ).pack(side=tk.LEFT, padx=5, ipady=10, ipadx=20)

    def _get_selected_article_id(self):
        """Get ID of selected article from tree"""
        if not hasattr(self, "articles_tree"):
            return None
        sel = self.articles_tree.selection()
        if not sel:
            return None
        values = self.articles_tree.item(sel[0], "values")
        if not values:
            return None
        short_id = values[0]
        return self._article_id_map.get(short_id)

    def show_articles(self):
        """Show articles management - FULL WIDTH"""
        self.clear_content()

        # Header
        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(
            header_frame,
            text="Article Management",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(side=tk.LEFT)

        # Action buttons
        actions = tk.Frame(header_frame, bg="white")
        actions.pack(side=tk.RIGHT)

        tk.Button(
            actions,
            text="+ Add New Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(side=tk.RIGHT, padx=5, ipady=6, ipadx=12)

        tk.Button(
            actions,
            text="✏️ Edit Selected",
            font=("Arial", 9),
            bg="#1f6feb",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_selected_article
        ).pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="🗑 Delete Selected",
            font=("Arial", 9),
            bg="#d1242f",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_selected_article
        ).pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=10)

        # Articles list - FULL WIDTH
        try:
            articles = self.db.get_all_articles()
            self._article_id_map = {}

            if articles:
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync")
                
                # Create frame for treeview and scrollbar
                tree_frame = tk.Frame(self.content_frame, bg="white")
                tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                
                self.articles_tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")

                # Column widths
                self.articles_tree.column("ID", width=100)
                self.articles_tree.column("Name", width=200)
                self.articles_tree.column("Mould", width=120)
                self.articles_tree.column("Size", width=100)
                self.articles_tree.column("Gender", width=100)
                self.articles_tree.column("Created By", width=120)
                self.articles_tree.column("Date", width=120)
                self.articles_tree.column("Sync", width=80)

                for col in columns:
                    self.articles_tree.heading(col, text=col)

                for article in articles:
                    short_id = article.id[:8]
                    self._article_id_map[short_id] = article.id
                    sync_status = "Synced" if article.sync_status == 1 else "Pending"
                    self.articles_tree.insert("", tk.END, values=(
                        short_id,
                        article.article_name,
                        article.mould,
                        article.size,
                        article.gender,
                        article.created_by[:8],
                        article.created_at.strftime("%Y-%m-%d"),
                        sync_status
                    ))

                # Scrollbar
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.articles_tree.yview)
                self.articles_tree.configure(yscroll=scrollbar.set)
                
                self.articles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    self.content_frame, 
                    text="No articles found", 
                    font=("Arial", 12), 
                    bg="white", 
                    fg="#999"
                ).pack(pady=40)

        except Exception as e:
            self.logger.error(f"Error loading articles: {e}")
            tk.Label(
                self.content_frame, 
                text=f"Error loading articles: {e}", 
                font=("Arial", 11), 
                bg="white", 
                fg="red"
            ).pack(pady=30)

    def edit_selected_article(self):
        """Edit selected article"""
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Edit", "Please select an article first")
            return
        messagebox.showinfo("Edit", f"Edit functionality for {article_id}")

    def delete_selected_article(self):
        """Delete selected article"""
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Delete", "Please select an article first")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete article {article_id}?"):
            if self.db.delete_article(article_id):
                messagebox.showinfo("Success", "Article deleted")
                self.show_articles()
            else:
                messagebox.showerror("Error", "Failed to delete article")

    def create_article(self):
        """Create new article dialog"""
        from db.models import Article

        dialog = tk.Toplevel(self.root)
        dialog.title("Create Article")
        dialog.geometry("500x650")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        article_id = self.generate_article_id()

        header = tk.Frame(dialog, bg=PRIMARY_COLOR)
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Create New Article", font=("Arial", 13, "bold"), 
                bg=PRIMARY_COLOR, fg="white").pack(pady=15)

        id_frame = tk.Frame(dialog, bg="#f0f0f0")
        id_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        tk.Label(id_frame, text=f"Article ID: {article_id}", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", fg=PRIMARY_COLOR).pack(pady=5)
        tk.Label(id_frame, text=f"Created by: {self.user['username']}", font=("Arial", 9), 
                bg="#f0f0f0", fg="#666").pack(pady=(0, 5))

        tk.Label(dialog, text="Article Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(5, 2))
        article_name_entry = tk.Entry(dialog, font=("Arial", 10), width=45)
        article_name_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Mould:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=45)
        mould_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Size:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=45)
        size_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Gender:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        gender_var = tk.StringVar(value="Unisex")
        gender_frame = tk.Frame(dialog)
        gender_frame.pack(anchor=tk.W, padx=20, pady=5)
        for gender in ["Male", "Female", "Unisex"]:
            tk.Radiobutton(gender_frame, text=gender, variable=gender_var, value=gender).pack(side=tk.LEFT, padx=5)

        tk.Label(dialog, text="Image (optional):", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        image_frame = tk.Frame(dialog)
        image_frame.pack(fill=tk.X, padx=20, pady=5)

        image_label = tk.Label(image_frame, text="No image selected", font=("Arial", 9), fg="gray")
        image_label.pack(side=tk.LEFT, padx=5)

        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Article Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            if file_path:
                self.selected_image_path = file_path
                filename = file_path.split('/')[-1].split('\\')[-1]
                image_label.config(text=filename, fg="green")

        tk.Button(
            image_frame,
            text="📷 Select Image",
            font=("Arial", 9),
            bg="#2196F3",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=select_image
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=10)

        status_label = tk.Label(dialog, text="", font=("Arial", 9), fg="blue")
        status_label.pack(pady=5)

        def save_article():
            try:
                article_name = article_name_entry.get().strip()
                mould = mould_entry.get().strip()
                size = size_entry.get().strip()
                gender = gender_var.get()

                if not all([article_name, mould, size]):
                    messagebox.showerror("Error", "Please fill all required fields")
                    return

                image_url = None
                if self.selected_image_path:
                    status_label.config(text="⏳ Uploading image...", fg="blue")
                    dialog.update()
                    image_url = self.ftp.upload_image(self.selected_image_path)
                    if image_url:
                        status_label.config(text="✅ Image uploaded!", fg="green")
                    dialog.update()

                article = Article(
                    id=article_id,
                    article_name=article_name,
                    mould=mould,
                    size=size,
                    gender=gender,
                    created_by=self.user['id'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    sync_status=0,
                    image_path=image_url
                )

                if self.db.add_article(article):
                    if self.firebase and self.firebase.is_connected():
                        synced = self.firebase.sync_articles([article.to_dict()])
                        if synced:
                            self.db.mark_article_synced(article.id)

                    messagebox.showinfo("Success", f"Article created!\nID: {article_id}")
                    dialog.destroy()
                    self.selected_image_path = None
                    self.show_articles()
                else:
                    messagebox.showerror("Error", "Failed to create article")

            except Exception as e:
                self.logger.error(f"Error creating article: {e}")
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(
            dialog,
            text="Save Article",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=save_article
        ).pack(pady=20, ipady=8, ipadx=30)

        dialog.wait_window()

    def add_user(self):
        messagebox.showinfo("Add User", "User creation dialog")

    def show_users(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Users Management", font=("Arial", 16, "bold"), bg="white").pack(pady=20)

    def show_sync_status(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Sync Status", font=("Arial", 16, "bold"), bg="white").pack(pady=20)

    def show_settings(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Settings", font=("Arial", 16, "bold"), bg="white").pack(pady=20)

    def show_about(self):
        self.clear_content()
        tk.Label(self.content_frame, text="About NEXUZY ARTICAL", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        tk.Label(self.content_frame, text="Version 2.1", font=("Arial", 11), bg="white").pack()

    def refresh_data(self):
        pass

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
