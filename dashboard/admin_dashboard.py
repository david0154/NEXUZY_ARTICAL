#!/usr/bin/env python3
"""Admin Dashboard - COMPLETE WORKING VERSION

All features:
- Proper window sizing (fills available space)
- Working export (PDF/Excel)
- FTP image upload
- Firebase sync
- Article/User management
- All buttons working
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os
import random
import string
import subprocess
import platform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR, APP_VERSION, DEVELOPER_NAME, DEVELOPER_EMAIL, COMPANY
from utils.export import ExportManager
from utils.ftp_uploader import get_ftp_uploader
from utils.security import hash_password
from db.models import Article, User
import uuid


class AdminDashboard:
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
        while True:
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            article_id = f"Fides-{random_part}"
            try:
                existing = self.db.get_article_by_id(article_id)
                if not existing:
                    return article_id
            except:
                return article_id

    def open_file(self, filepath):
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            self.logger.error(f"Failed to open file: {e}")

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top bar
        top_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        tk.Label(
            top_frame,
            text=f"{APP_NAME} - Admin Dashboard",
            font=("Arial", 14, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            top_frame,
            text=f"Welcome, {self.user['username']} ({self.user['role'].upper()}) 👤",
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

        # FIXED: Content frame directly without canvas - fills 100% space
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Dashboard Overview",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(0, 20))

        try:
            total_users = len(self.db.get_all_users())
            total_articles = self.db.get_articles_count()
            pending_sync = self.db.get_pending_articles_count()
            is_online = self.network_checker.is_connected()
        except Exception as e:
            self.logger.error(f"Error fetching stats: {e}")
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
        self.clear_content()

        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="Article Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)

        actions = tk.Frame(header_frame, bg="white")
        actions.pack(side=tk.RIGHT)

        tk.Button(
            actions,
            text="📄 Export PDF",
            font=("Arial", 9),
            bg="#d32f2f",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_articles_pdf
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="📊 Export Excel",
            font=("Arial", 9),
            bg="#388e3c",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_articles_excel
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="+ Add Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(side=tk.RIGHT, padx=3, ipady=6, ipadx=12)

        tk.Button(
            actions,
            text="✏️ Edit",
            font=("Arial", 9),
            bg="#1f6feb",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_selected_article
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="🗑 Delete",
            font=("Arial", 9),
            bg="#d1242f",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_selected_article
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        try:
            articles = self.db.get_all_articles()
            self._article_id_map = {}

            if articles:
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync")

                tree_frame = tk.Frame(self.content_frame, bg="white")
                tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

                self.articles_tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")

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
                text=f"Error: {e}",
                font=("Arial", 11),
                bg="white",
                fg="red"
            ).pack(pady=30)

    def edit_selected_article(self):
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Edit", "Please select an article first")
            return

        article = self.db.get_article_by_id(article_id)
        if not article:
            messagebox.showerror("Edit", "Article not found")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Article")
        dialog.geometry("450x520")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Edit Article", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Article Name:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        name_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        name_entry.insert(0, article.article_name)
        name_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Mould:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        mould_entry.insert(0, article.mould)
        mould_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Size:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        size_entry.insert(0, article.size)
        size_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Gender:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        gender_var = tk.StringVar(value=article.gender)
        gender_frame = tk.Frame(dialog)
        gender_frame.pack(anchor=tk.W, padx=20)
        for gender in ["Male", "Female", "Unisex"]:
            tk.Radiobutton(gender_frame, text=gender, variable=gender_var, value=gender).pack(side=tk.LEFT, padx=5)

        image_path_var = tk.StringVar(value=article.image_path or "")

        tk.Label(dialog, text="Image:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        image_frame = tk.Frame(dialog)
        image_frame.pack(fill=tk.X, padx=20)

        image_entry = tk.Entry(image_frame, textvariable=image_path_var, font=("Arial", 9), width=30, state="readonly")
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        def browse_image():
            path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
            )
            if path:
                image_path_var.set(path)

        tk.Button(image_frame, text="Browse", command=browse_image).pack(side=tk.LEFT, padx=5)

        def save_changes():
            try:
                self.db.update_article(
                    article_id,
                    name_entry.get().strip(),
                    mould_entry.get().strip(),
                    size_entry.get().strip(),
                    gender_var.get(),
                    image_path_var.get() or None,
                )

                if self.firebase and self.firebase.is_connected():
                    updates = {
                        'article_name': name_entry.get().strip(),
                        'mould': mould_entry.get().strip(),
                        'size': size_entry.get().strip(),
                        'gender': gender_var.get(),
                        'image_path': image_path_var.get() or None,
                    }
                    self.firebase.update_article(article_id, updates)
                    self.db.mark_article_synced(article_id)

                messagebox.showinfo("Success", "Article updated")
                dialog.destroy()
                self.show_articles()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(
            dialog,
            text="Save Changes",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            command=save_changes
        ).pack(pady=20, ipady=6, ipadx=30)

        dialog.wait_window()

    def delete_selected_article(self):
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Delete", "Please select an article first")
            return

        if not messagebox.askyesno("Delete", "Delete this article?"):
            return

        try:
            self.db.delete_article(article_id)
            if self.firebase and self.firebase.is_connected():
                self.firebase.delete_article(article_id)

            messagebox.showinfo("Success", "Article deleted")
            self.show_articles()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def create_article(self):
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
        dialog = tk.Toplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Add New User", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Username:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        username_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        username_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Password:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        password_entry = tk.Entry(dialog, font=("Arial", 10), width=35, show="•")
        password_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Role:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        role_var = tk.StringVar(value="user")
        role_frame = tk.Frame(dialog)
        role_frame.pack(anchor=tk.W, padx=20)
        tk.Radiobutton(role_frame, text="User", variable=role_var, value="user").pack(side=tk.LEFT)
        tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin").pack(side=tk.LEFT, padx=20)

        def save_user():
            try:
                username = username_entry.get().strip()
                password = password_entry.get()
                role = role_var.get()

                if not username or not password:
                    messagebox.showerror("Error", "Username and password required")
                    return

                if len(password) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters")
                    return

                user = User(
                    id=str(uuid.uuid4()),
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    created_at=datetime.now(),
                    last_login=None
                )

                if self.db.add_user(user):
                    if self.firebase and self.firebase.is_connected():
                        self.firebase.create_user(user.id, username, password, role)

                    messagebox.showinfo("Success", f"User '{username}' created")
                    dialog.destroy()
                    self.show_users()
                else:
                    messagebox.showerror("Error", "Failed (username may exist)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

        tk.Button(
            dialog,
            text="Create User",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            command=save_user
        ).pack(pady=20, ipady=6, ipadx=30)

        dialog.wait_window()

    def show_users(self):
        self.clear_content()

        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="User Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)

        actions = tk.Frame(header_frame, bg="white")
        actions.pack(side=tk.RIGHT)

        tk.Button(
            actions,
            text="📄 Export PDF",
            font=("Arial", 9),
            bg="#d32f2f",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_users_pdf
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="📊 Export Excel",
            font=("Arial", 9),
            bg="#388e3c",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_users_excel
        ).pack(side=tk.RIGHT, padx=3, ipady=5, ipadx=10)

        tk.Button(
            actions,
            text="+ Add User",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_user
        ).pack(side=tk.RIGHT, padx=3, ipady=6, ipadx=12)

        try:
            users = self.db.get_all_users()
            if users:
                columns = ("Username", "Role", "Last Login", "Created")

                tree_frame = tk.Frame(self.content_frame, bg="white")
                tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

                tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")

                for col in columns:
                    tree.column(col, width=150)
                    tree.heading(col, text=col)

                for user in users:
                    last_login = user.last_login.strftime("%Y-%m-%d") if user.last_login else "Never"
                    created = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
                    tree.insert("", tk.END, values=(user.username, user.role.upper(), last_login, created))

                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)

                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    self.content_frame,
                    text="No users found",
                    font=("Arial", 11),
                    bg="white",
                    fg="#999"
                ).pack(pady=20)
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            tk.Label(
                self.content_frame,
                text=f"Error: {e}",
                font=("Arial", 10),
                bg="white",
                fg="red"
            ).pack(pady=20)

    def show_sync_status(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Synchronization Status",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 20))

        is_online = self.network_checker.is_connected()
        firebase_init = self.firebase.initialized if self.firebase else False

        status_text = "✅ Online - Ready to sync" if is_online and firebase_init else "❌ Offline"
        status_color = "green" if is_online and firebase_init else "orange"

        tk.Label(
            self.content_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            bg="white",
            fg=status_color
        ).pack(anchor=tk.W, pady=10)

        try:
            pending_count = self.db.get_pending_articles_count()
            total_count = self.db.get_articles_count()
            synced_count = total_count - pending_count

            stats_frame = tk.Frame(self.content_frame, bg="#f9f9f9", relief=tk.FLAT, bd=1)
            stats_frame.pack(fill=tk.X, pady=15, padx=10)

            tk.Label(stats_frame, text=f"Total Articles: {total_count}", font=("Arial", 10), bg="#f9f9f9").pack(anchor=tk.W, padx=15, pady=5)
            tk.Label(stats_frame, text=f"Synced: {synced_count}", font=("Arial", 10), bg="#f9f9f9", fg="green").pack(anchor=tk.W, padx=15, pady=5)
            tk.Label(stats_frame, text=f"Pending: {pending_count}", font=("Arial", 10), bg="#f9f9f9", fg="orange" if pending_count > 0 else "green").pack(anchor=tk.W, padx=15, pady=5)
        except Exception as e:
            self.logger.error(f"Error getting sync stats: {e}")

        if is_online and firebase_init:
            tk.Button(
                self.content_frame,
                text="🔄 Sync Now",
                font=("Arial", 10),
                bg=PRIMARY_COLOR,
                fg="white",
                relief=tk.FLAT,
                cursor="hand2",
                command=self.sync_data
            ).pack(anchor=tk.W, pady=10, ipady=6, ipadx=15)

    def show_settings(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="Settings",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 20))

        tk.Label(
            self.content_frame,
            text="Application Settings",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 5))

        settings = [
            ("App Name", APP_NAME),
            ("Version", APP_VERSION),
            ("User", self.user['username']),
            ("Role", self.user['role'].upper()),
        ]

        for label, value in settings:
            frame = tk.Frame(self.content_frame, bg="white")
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{label}:", font=("Arial", 10), bg="white", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 10), bg="white", fg="#666").pack(side=tk.LEFT)

    def show_about(self):
        self.clear_content()

        tk.Label(
            self.content_frame,
            text="About",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(0, 20))

        tk.Label(
            self.content_frame,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 5))

        tk.Label(
            self.content_frame,
            text=f"Company: {COMPANY}",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 2))

        tk.Label(
            self.content_frame,
            text=f"Developer: {DEVELOPER_NAME}",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 2))

        tk.Label(
            self.content_frame,
            text=f"Contact: {DEVELOPER_EMAIL}",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 10))

        repo_link = tk.Label(
            self.content_frame,
            text="github.com/david0154/NEXUZY_ARTICAL",
            font=("Arial", 10, "underline"),
            bg="white",
            fg="#1f6feb",
            cursor="hand2"
        )
        repo_link.pack(anchor=tk.W, pady=(0, 10))

        def open_repo(event=None):
            import webbrowser
            webbrowser.open("https://github.com/david0154/NEXUZY_ARTICAL")

        repo_link.bind("<Button-1>", open_repo)

    def sync_data(self):
        try:
            if not self.firebase or not self.firebase.is_connected():
                messagebox.showwarning("Sync", "Cannot sync: Firebase not available")
                return

            pending_articles = self.db.get_pending_articles()
            if pending_articles:
                articles_dict = [article.to_dict() for article in pending_articles]
                synced_count = self.firebase.sync_articles(articles_dict)
                for article in pending_articles[:synced_count]:
                    self.db.mark_article_synced(article.id)

                messagebox.showinfo("Sync", f"Synced {synced_count} article(s)")
                self.show_sync_status()
            else:
                messagebox.showinfo("Sync", "All articles synced")
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed: {e}")

    def refresh_data(self):
        try:
            if self.firebase and self.firebase.is_connected():
                pending = self.db.get_pending_articles()
                if pending:
                    articles_dict = [a.to_dict() for a in pending]
                    synced = self.firebase.sync_articles(articles_dict)
                    for article in pending[:synced]:
                        self.db.mark_article_synced(article.id)
        except Exception as e:
            self.logger.debug(f"Auto-sync error: {e}")
        self.root.after(30000, self.refresh_data)

    def export_articles_excel(self):
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return

            articles_dict = []
            for article in articles:
                articles_dict.append({
                    'id': article.id,
                    'article_name': article.article_name,
                    'mould': article.mould,
                    'size': article.size,
                    'gender': article.gender,
                    'created_by': article.created_by,
                    'created_at': article.created_at.strftime('%Y-%m-%d'),
                    'updated_at': article.updated_at.strftime('%Y-%m-%d'),
                    'sync_status': article.sync_status
                })

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not file_path:
                return

            path = self.exporter.export_articles_to_excel(articles_dict, output_path=file_path)
            result = messagebox.askyesno("Export", f"Exported to Excel!\n\nOpen file?")

            if result:
                self.open_file(path)
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl:\npip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def export_articles_pdf(self):
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return

            articles_dict = []
            for article in articles:
                articles_dict.append({
                    'id': article.id,
                    'article_name': article.article_name,
                    'mould': article.mould,
                    'size': article.size,
                    'gender': article.gender,
                    'created_by': article.created_by,
                    'created_at': article.created_at.strftime('%Y-%m-%d'),
                    'updated_at': article.updated_at.strftime('%Y-%m-%d'),
                    'sync_status': article.sync_status
                })

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            if not file_path:
                return

            path = self.exporter.export_articles_to_pdf(articles_dict, output_path=file_path)
            result = messagebox.askyesno("Export", f"Exported to PDF!\n\nOpen file?")

            if result:
                self.open_file(path)
        except ImportError:
            messagebox.showerror("Error", "Install reportlab:\npip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def export_users_excel(self):
        try:
            users = self.db.get_all_users()
            if not users:
                messagebox.showinfo("Export", "No users to export")
                return

            users_dict = []
            for user in users:
                user_data = user.to_dict()
                user_data.pop('password_hash', None)
                users_dict.append(user_data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not file_path:
                return

            path = self.exporter.export_users_to_excel(users_dict, output_path=file_path)
            result = messagebox.askyesno("Export", f"Exported to Excel!\n\nOpen file?")

            if result:
                self.open_file(path)
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl:\npip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def export_users_pdf(self):
        try:
            users = self.db.get_all_users()
            if not users:
                messagebox.showinfo("Export", "No users to export")
                return

            users_dict = []
            for user in users:
                user_data = user.to_dict()
                user_data.pop('password_hash', None)
                users_dict.append(user_data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            if not file_path:
                return

            path = self.exporter.export_users_to_pdf(users_dict, output_path=file_path)
            result = messagebox.askyesno("Export", f"Exported to PDF!\n\nOpen file?")

            if result:
                self.open_file(path)
        except ImportError:
            messagebox.showerror("Error", "Install reportlab:\npip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
