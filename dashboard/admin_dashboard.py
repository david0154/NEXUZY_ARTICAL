#!/usr/bin/env python3
"""
Admin Dashboard Module
Full control panel for administrators
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR
from utils.export import ExportManager


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

        self.root.deiconify()
        self.setup_ui()
        self.refresh_data()
        self.logger.info(f"Admin dashboard initialized for user: {user['username']}")

    def setup_ui(self):
        """Create admin dashboard UI"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()

        # Top bar
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
            text=f"Welcome, {self.user['username']} ({self.user['role'].upper()})",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        user_info.pack(side=tk.RIGHT, padx=20, pady=10)

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
            ("⚙️ Settings", self.show_settings),
            ("🚺 Logout", self.logout),
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

        # Show dashboard by default
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

        # Statistics
        try:
            total_users = len(self.db.get_all_users())
            total_articles = self.db.get_articles_count()
            pending_sync = self.db.get_pending_articles_count()
            is_online = self.network_checker.is_connected()
        except Exception as e:
            self.logger.error(f"Error fetching dashboard stats: {e}")
            total_users = 0
            total_articles = 0
            pending_sync = 0
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
            stat_card = tk.Frame(stats_frame, bg="#f9f9f9", relief=tk.FLAT, bd=1)
            stat_card.pack(fill=tk.X, pady=5, padx=10)

            tk.Label(stat_card, text=f"{emoji} {label}: {value}", font=("Arial", 12), bg="#f9f9f9").pack(anchor=tk.W, padx=15, pady=10)

        # Quick actions
        tk.Label(
            self.content_frame,
            text="Quick Actions",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(20, 10))

        tk.Button(
            self.content_frame,
            text="+ Create New Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(fill=tk.X, pady=5, ipady=8)

        tk.Button(
            self.content_frame,
            text="+ Add User",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_user
        ).pack(fill=tk.X, pady=5, ipady=8)

    def _get_selected_article_id(self):
        if not hasattr(self, "articles_tree"):
            return None
        sel = self.articles_tree.selection()
        if not sel:
            return None
        values = self.articles_tree.item(sel[0], "values")
        if not values:
            return None
        # We store 8-char short id in UI; keep full id mapping
        short_id = values[0]
        return self._article_id_map.get(short_id)

    def show_articles(self):
        """Show articles management"""
        self.clear_content()

        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X)

        title = tk.Label(
            header_frame,
            text="Article Management",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(side=tk.LEFT, pady=(0, 15))

        # Actions
        actions = tk.Frame(header_frame, bg="white")
        actions.pack(side=tk.RIGHT, pady=(0, 15))

        tk.Button(
            actions,
            text="✏️ Edit Selected",
            font=("Arial", 9),
            bg="#1f6feb",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_selected_article
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)

        tk.Button(
            actions,
            text="🗑 Delete Selected",
            font=("Arial", 9),
            bg="#d1242f",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_selected_article
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)

        # Export buttons
        export_frame = tk.Frame(self.content_frame, bg="white")
        export_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            export_frame,
            text="📊 Export Excel",
            font=("Arial", 9),
            bg="#2c974b",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_articles_excel
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)

        tk.Button(
            export_frame,
            text="📄 Export PDF",
            font=("Arial", 9),
            bg="#d35400",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_articles_pdf
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)

        tk.Button(
            export_frame,
            text="+ Add New Article",
            font=("Arial", 9),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(side=tk.RIGHT, padx=5, ipady=4, ipadx=10)

        # Articles list
        try:
            articles = self.db.get_all_articles()
            self._article_id_map = {}

            if articles:
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync")
                self.articles_tree = ttk.Treeview(self.content_frame, columns=columns, height=15, show="headings")

                self.articles_tree.column("ID", width=80)
                self.articles_tree.column("Name", width=160)
                self.articles_tree.column("Mould", width=100)
                self.articles_tree.column("Size", width=100)
                self.articles_tree.column("Gender", width=80)
                self.articles_tree.column("Created By", width=110)
                self.articles_tree.column("Date", width=100)
                self.articles_tree.column("Sync", width=70)

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

                self.articles_tree.pack(fill=tk.BOTH, expand=True)

                scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.articles_tree.yview)
                self.articles_tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(self.content_frame, text="No articles found", font=("Arial", 11), bg="white", fg="#999").pack(pady=20)

        except Exception as e:
            self.logger.error(f"Error loading articles: {e}")
            tk.Label(self.content_frame, text=f"Error loading articles: {e}", font=("Arial", 10), bg="white", fg="red").pack(pady=20)

    def edit_selected_article(self):
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Edit", "Please select an article first")
            return

        article = self.db.get_article_by_id(article_id)
        if not article:
            messagebox.showerror("Edit", "Selected article not found")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Article")
        dialog.geometry("420x420")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Edit Article", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Article Name:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        name_entry = tk.Entry(dialog, font=("Arial", 10), width=38)
        name_entry.insert(0, article.article_name)
        name_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Mould:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=38)
        mould_entry.insert(0, article.mould)
        mould_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Size:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=38)
        size_entry.insert(0, article.size)
        size_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Gender:").pack(anchor=tk.W, padx=20, pady=(10, 3))
        gender_var = tk.StringVar(value=article.gender)
        gender_frame = tk.Frame(dialog)
        gender_frame.pack(anchor=tk.W, padx=20)
        for gender in ["Male", "Female", "Unisex"]:
            tk.Radiobutton(gender_frame, text=gender, variable=gender_var, value=gender).pack(side=tk.LEFT, padx=5)

        def save_changes():
            try:
                ok = self.db.update_article(
                    article_id,
                    name_entry.get().strip(),
                    mould_entry.get().strip(),
                    size_entry.get().strip(),
                    gender_var.get()
                )
                if not ok:
                    messagebox.showerror("Edit", "Failed to update article")
                    return

                # Firebase sync (update)
                if self.firebase and self.firebase.is_connected():
                    self.firebase.update_article(article_id, {
                        'article_name': name_entry.get().strip(),
                        'mould': mould_entry.get().strip(),
                        'size': size_entry.get().strip(),
                        'gender': gender_var.get(),
                    })
                    self.db.mark_article_synced(article_id)

                messagebox.showinfo("Edit", "Article updated successfully")
                dialog.destroy()
                self.show_articles()
            except Exception as e:
                self.logger.error(f"Edit article failed: {e}")
                messagebox.showerror("Edit", f"Failed: {e}")

        tk.Button(dialog, text="Save Changes", font=("Arial", 10), bg=PRIMARY_COLOR, fg="white", command=save_changes).pack(pady=20, ipady=6, ipadx=30)

    def delete_selected_article(self):
        article_id = self._get_selected_article_id()
        if not article_id:
            messagebox.showwarning("Delete", "Please select an article first")
            return

        if not messagebox.askyesno("Delete", "Are you sure you want to delete this article?"):
            return

        try:
            ok = self.db.delete_article(article_id)
            if not ok:
                messagebox.showerror("Delete", "Failed to delete article locally")
                return

            # Firebase delete
            if self.firebase and self.firebase.is_connected():
                self.firebase.delete_article(article_id)

            messagebox.showinfo("Delete", "Article deleted successfully")
            self.show_articles()
        except Exception as e:
            self.logger.error(f"Delete article failed: {e}")
            messagebox.showerror("Delete", f"Failed: {e}")

    def create_article(self):
        """Create new article dialog"""
        import uuid
        from db.models import Article

        dialog = tk.Toplevel(self.root)
        dialog.title("Create Article")
        dialog.geometry("400x400")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Create New Article", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Article Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        article_name_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        article_name_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Mould:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        mould_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Size:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        size_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Gender:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        gender_var = tk.StringVar(value="Unisex")
        gender_frame = tk.Frame(dialog)
        gender_frame.pack(anchor=tk.W, padx=20)

        for gender in ["Male", "Female", "Unisex"]:
            tk.Radiobutton(gender_frame, text=gender, variable=gender_var, value=gender).pack(side=tk.LEFT, padx=5)

        def save_article():
            try:
                article_name = article_name_entry.get().strip()
                mould = mould_entry.get().strip()
                size = size_entry.get().strip()
                gender = gender_var.get()

                if not article_name or not mould:
                    messagebox.showerror("Error", "Article name and mould are required")
                    return

                if not size:
                    messagebox.showerror("Error", "Size is required")
                    return

                article = Article(
                    id=str(uuid.uuid4()),
                    article_name=article_name,
                    mould=mould,
                    size=size,
                    gender=gender,
                    created_by=self.user['id'],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    sync_status=0
                )

                if self.db.add_article(article):
                    # Auto sync immediately
                    if self.firebase and self.firebase.is_connected():
                        synced = self.firebase.sync_articles([article.to_dict()])
                        if synced:
                            self.db.mark_article_synced(article.id)

                    messagebox.showinfo("Success", "Article created successfully")
                    dialog.destroy()
                    self.show_articles()
                else:
                    messagebox.showerror("Error", "Failed to create article")
            except Exception as e:
                self.logger.error(f"Error creating article: {e}")
                messagebox.showerror("Error", f"Failed to create article: {e}")

        tk.Button(dialog, text="Save Article", font=("Arial", 10), bg=PRIMARY_COLOR, fg="white", command=save_article).pack(pady=20, ipady=6, ipadx=30)

    # ---- other methods below are unchanged from previous file ----

    def add_user(self):
        from utils.security import hash_password
        from db.models import User
        import uuid

        dialog = tk.Toplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("400x300")
        dialog.resizable(False, False)

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
                    messagebox.showerror("Error", "Username and password are required")
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

                    messagebox.showinfo("Success", f"User '{username}' created successfully")
                    dialog.destroy()
                    self.show_users()
                else:
                    messagebox.showerror("Error", "Failed to add user (username may already exist)")
            except Exception as e:
                self.logger.error(f"Error adding user: {e}")
                messagebox.showerror("Error", f"Failed to add user: {e}")

        tk.Button(dialog, text="Create User", font=("Arial", 10), bg=PRIMARY_COLOR, fg="white", command=save_user).pack(pady=20, ipady=6, ipadx=30)

    # Remaining methods are same as before (users, sync status, export, refresh, logout)

    def show_users(self):
        # unchanged from previous version
        self.clear_content()
        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X)
        title = tk.Label(header_frame, text="User Management", font=("Arial", 16, "bold"), bg="white")
        title.pack(side=tk.LEFT, pady=(0, 15))
        export_frame = tk.Frame(header_frame, bg="white")
        export_frame.pack(side=tk.RIGHT, pady=(0, 15))
        tk.Button(export_frame, text="📊 Export Excel", font=("Arial", 9), bg="#2c974b", fg="white", relief=tk.FLAT, cursor="hand2", command=self.export_users_excel).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        tk.Button(export_frame, text="📄 Export PDF", font=("Arial", 9), bg="#d35400", fg="white", relief=tk.FLAT, cursor="hand2", command=self.export_users_pdf).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        tk.Button(self.content_frame, text="+ Add New User", font=("Arial", 10), bg=PRIMARY_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=self.add_user).pack(anchor=tk.W, pady=(10, 15), ipady=6, ipadx=15)
        try:
            users = self.db.get_all_users()
            if users:
                columns = ("Username", "Role", "Last Login", "Created")
                tree = ttk.Treeview(self.content_frame, columns=columns, height=15, show="headings")
                for col in columns:
                    tree.column(col, width=120)
                    tree.heading(col, text=col)
                for user in users:
                    last_login = user.last_login.strftime("%Y-%m-%d") if user.last_login else "Never"
                    created = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
                    tree.insert("", tk.END, values=(user.username, user.role.upper(), last_login, created))
                tree.pack(fill=tk.BOTH, expand=True)
                scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(self.content_frame, text="No users found", font=("Arial", 11), bg="white", fg="#999").pack(pady=20)
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            tk.Label(self.content_frame, text=f"Error: {e}", font=("Arial", 10), bg="white", fg="red").pack(pady=20)

    def show_sync_status(self):
        # unchanged
        self.clear_content()
        title = tk.Label(self.content_frame, text="Synchronization Status", font=("Arial", 16, "bold"), bg="white")
        title.pack(anchor=tk.W, pady=(0, 20))
        is_online = self.network_checker.is_connected()
        firebase_initialized = self.firebase.initialized if self.firebase else False
        status_text = "✅ Online - Ready to sync" if is_online and firebase_initialized else "❌ Offline - Local only"
        status_color = "green" if is_online and firebase_initialized else "orange"
        tk.Label(self.content_frame, text=status_text, font=("Arial", 12, "bold"), bg="white", fg=status_color).pack(anchor=tk.W, pady=10)
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
        if is_online and firebase_initialized:
            tk.Button(self.content_frame, text="🔄 Sync Now", font=("Arial", 10), bg=PRIMARY_COLOR, fg="white", relief=tk.FLAT, cursor="hand2", command=self.sync_data).pack(anchor=tk.W, pady=10, ipady=6, ipadx=15)
        else:
            tk.Label(self.content_frame, text="⚠️ Cannot sync: " + ("No internet connection" if not is_online else "Firebase not configured"), font=("Arial", 10), bg="white", fg="orange").pack(anchor=tk.W, pady=10)

    def show_settings(self):
        self.clear_content()
        title = tk.Label(self.content_frame, text="Settings", font=("Arial", 16, "bold"), bg="white")
        title.pack(anchor=tk.W, pady=(0, 20))
        tk.Label(self.content_frame, text="Application Settings", font=("Arial", 11, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 5))
        settings = [("App Name", APP_NAME), ("User", self.user['username']), ("Role", self.user['role'].upper()), ("User ID", self.user.get('id', 'N/A')[:16])]
        for label, value in settings:
            frame = tk.Frame(self.content_frame, bg="white")
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{label}:", font=("Arial", 10), bg="white", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 10), bg="white", fg="#666").pack(side=tk.LEFT)

    def sync_data(self):
        try:
            if not self.firebase or not self.firebase.is_connected():
                messagebox.showwarning("Sync", "Cannot sync: Firebase not available or no internet")
                return
            pending_articles = self.db.get_pending_articles()
            if pending_articles:
                articles_dict = [article.to_dict() for article in pending_articles]
                synced_count = self.firebase.sync_articles(articles_dict)
                for article in pending_articles[:synced_count]:
                    self.db.mark_article_synced(article.id)
                messagebox.showinfo("Sync", f"Successfully synced {synced_count} article(s)")
                self.show_sync_status()
            else:
                messagebox.showinfo("Sync", "All articles are already synced")
            self.logger.info(f"Manual sync completed: {len(pending_articles)} articles")
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            messagebox.showerror("Sync Error", f"Failed to sync data: {e}")

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
            articles_dict = [article.to_dict() for article in articles]
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Articles Excel", initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            if not file_path:
                return
            path = self.exporter.export_articles_to_excel(articles_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to Excel:\n{path}")
            self.logger.info(f"Articles exported to Excel: {path}")
        except Exception as e:
            self.logger.error(f"Export articles Excel failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export articles to Excel:\n{e}")

    def export_articles_pdf(self):
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return
            articles_dict = [article.to_dict() for article in articles]
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save Articles PDF", initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if not file_path:
                return
            path = self.exporter.export_articles_to_pdf(articles_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to PDF:\n{path}")
            self.logger.info(f"Articles exported to PDF: {path}")
        except Exception as e:
            self.logger.error(f"Export articles PDF failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export articles to PDF:\n{e}")

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
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Users Excel", initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            if not file_path:
                return
            path = self.exporter.export_users_to_excel(users_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to Excel:\n{path}")
            self.logger.info(f"Users exported to Excel: {path}")
        except Exception as e:
            self.logger.error(f"Export users Excel failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export users to Excel:\n{e}")

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
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save Users PDF", initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if not file_path:
                return
            path = self.exporter.export_users_to_pdf(users_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to PDF:\n{path}")
            self.logger.info(f"Users exported to PDF: {path}")
        except Exception as e:
            self.logger.error(f"Export users PDF failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export users to PDF:\n{e}")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
