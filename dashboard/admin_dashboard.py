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
        
        # Export buttons
        export_frame = tk.Frame(header_frame, bg="white")
        export_frame.pack(side=tk.RIGHT, pady=(0, 15))
        
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
        
        # Add button
        tk.Button(
            self.content_frame,
            text="+ Add New Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(anchor=tk.W, pady=(10, 15), ipady=6, ipadx=15)
        
        # Articles list
        try:
            articles = self.db.get_all_articles()
            if articles:
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync")
                tree = ttk.Treeview(self.content_frame, columns=columns, height=15, show="headings")
                
                # Column widths
                tree.column("ID", width=80)
                tree.column("Name", width=150)
                tree.column("Mould", width=100)
                tree.column("Size", width=100)
                tree.column("Gender", width=80)
                tree.column("Created By", width=100)
                tree.column("Date", width=100)
                tree.column("Sync", width=70)
                
                for col in columns:
                    tree.heading(col, text=col)
                
                for article in articles:
                    sync_status = "Synced" if article.sync_status == 1 else "Pending"
                    tree.insert("", tk.END, values=(
                        article.id[:8],
                        article.article_name,
                        article.mould,
                        article.size,
                        article.gender,
                        article.created_by[:8],
                        article.created_at.strftime("%Y-%m-%d"),
                        sync_status
                    ))
                
                tree.pack(fill=tk.BOTH, expand=True)
                
                scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    self.content_frame,
                    text="No articles found",
                    font=("Arial", 11),
                    bg="white",
                    fg="#999"
                ).pack(pady=20)
        except Exception as e:
            self.logger.error(f"Error loading articles: {e}")
            tk.Label(
                self.content_frame,
                text=f"Error loading articles: {e}",
                font=("Arial", 10),
                bg="white",
                fg="red"
            ).pack(pady=20)

    def show_users(self):
        """Show users management"""
        self.clear_content()
        
        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(
            header_frame,
            text="User Management",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(side=tk.LEFT, pady=(0, 15))
        
        # Export buttons
        export_frame = tk.Frame(header_frame, bg="white")
        export_frame.pack(side=tk.RIGHT, pady=(0, 15))
        
        tk.Button(
            export_frame,
            text="📊 Export Excel",
            font=("Arial", 9),
            bg="#2c974b",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_users_excel
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        
        tk.Button(
            export_frame,
            text="📄 Export PDF",
            font=("Arial", 9),
            bg="#d35400",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_users_pdf
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        
        # Add button
        tk.Button(
            self.content_frame,
            text="+ Add New User",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_user
        ).pack(anchor=tk.W, pady=(10, 15), ipady=6, ipadx=15)
        
        # Users list
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
                    
                    tree.insert("", tk.END, values=(
                        user.username,
                        user.role.upper(),
                        last_login,
                        created
                    ))
                
                tree.pack(fill=tk.BOTH, expand=True)
                
                scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
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
        """Show synchronization status"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Synchronization Status",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        is_online = self.network_checker.is_connected()
        firebase_initialized = self.firebase.initialized if self.firebase else False
        
        status_text = "✅ Online - Ready to sync" if is_online and firebase_initialized else "❌ Offline - Local only"
        status_color = "green" if is_online and firebase_initialized else "orange"
        
        status_label = tk.Label(
            self.content_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            bg="white",
            fg=status_color
        )
        status_label.pack(anchor=tk.W, pady=10)
        
        # Sync statistics
        try:
            pending_count = self.db.get_pending_articles_count()
            total_count = self.db.get_articles_count()
            synced_count = total_count - pending_count
            
            stats_frame = tk.Frame(self.content_frame, bg="#f9f9f9", relief=tk.FLAT, bd=1)
            stats_frame.pack(fill=tk.X, pady=15, padx=10)
            
            tk.Label(
                stats_frame,
                text=f"Total Articles: {total_count}",
                font=("Arial", 10),
                bg="#f9f9f9"
            ).pack(anchor=tk.W, padx=15, pady=5)
            
            tk.Label(
                stats_frame,
                text=f"Synced: {synced_count}",
                font=("Arial", 10),
                bg="#f9f9f9",
                fg="green"
            ).pack(anchor=tk.W, padx=15, pady=5)
            
            tk.Label(
                stats_frame,
                text=f"Pending: {pending_count}",
                font=("Arial", 10),
                bg="#f9f9f9",
                fg="orange" if pending_count > 0 else "green"
            ).pack(anchor=tk.W, padx=15, pady=5)
        except Exception as e:
            self.logger.error(f"Error getting sync stats: {e}")
        
        if is_online and firebase_initialized:
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
        else:
            tk.Label(
                self.content_frame,
                text="⚠️ Cannot sync: " + ("No internet connection" if not is_online else "Firebase not configured"),
                font=("Arial", 10),
                bg="white",
                fg="orange"
            ).pack(anchor=tk.W, pady=10)

    def show_settings(self):
        """Show settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Settings",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(
            self.content_frame,
            text="Application Settings",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        settings = [
            ("App Name", APP_NAME),
            ("User", self.user['username']),
            ("Role", self.user['role'].upper()),
            ("User ID", self.user.get('id', 'N/A')[:16]),
        ]
        
        for label, value in settings:
            frame = tk.Frame(self.content_frame, bg="white")
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{label}:", font=("Arial", 10), bg="white", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 10), bg="white", fg="#666").pack(side=tk.LEFT)

    def create_article(self):
        """Create new article dialog"""
        import uuid
        from db.models import Article
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Article")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Create New Article", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Article Name
        tk.Label(dialog, text="Article Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        article_name_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        article_name_entry.pack(padx=20, ipady=5)
        
        # Mould
        tk.Label(dialog, text="Mould:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        mould_entry.pack(padx=20, ipady=5)
        
        # Size - CHANGED TO TEXT BOX
        tk.Label(dialog, text="Size:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=35)
        size_entry.pack(padx=20, ipady=5)
        
        # Gender
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
                    messagebox.showinfo("Success", "Article created successfully")
                    dialog.destroy()
                    self.show_articles()
                else:
                    messagebox.showerror("Error", "Failed to create article")
            except Exception as e:
                self.logger.error(f"Error creating article: {e}")
                messagebox.showerror("Error", f"Failed to create article: {e}")
        
        tk.Button(
            dialog,
            text="Save Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            command=save_article
        ).pack(pady=20, ipady=6, ipadx=30)

    def add_user(self):
        """Add new user dialog"""
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
                    # Try to sync to Firebase if online
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
        
        tk.Button(
            dialog,
            text="Create User",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            command=save_user
        ).pack(pady=20, ipady=6, ipadx=30)

    def sync_data(self):
        """Sync data with Firebase"""
        try:
            if not self.firebase or not self.firebase.is_connected():
                messagebox.showwarning("Sync", "Cannot sync: Firebase not available or no internet")
                return
            
            # Sync pending articles
            pending_articles = self.db.get_pending_articles()
            if pending_articles:
                articles_dict = [article.to_dict() for article in pending_articles]
                synced_count = self.firebase.sync_articles(articles_dict)
                
                # Mark synced articles
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
        """Refresh dashboard data periodically"""
        try:
            if self.firebase and self.firebase.is_connected():
                # Auto-sync in background
                pending = self.db.get_pending_articles()
                if pending:
                    articles_dict = [a.to_dict() for a in pending]
                    synced = self.firebase.sync_articles(articles_dict)
                    for article in pending[:synced]:
                        self.db.mark_article_synced(article.id)
        except Exception as e:
            self.logger.debug(f"Auto-sync error: {e}")
        
        # Schedule next refresh
        self.root.after(30000, self.refresh_data)

    def export_articles_excel(self):
        """Export articles to Excel"""
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return
            
            # Convert Article objects to dictionaries
            articles_dict = [article.to_dict() for article in articles]
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Save Articles Excel",
                initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            if not file_path:
                return
            
            path = self.exporter.export_articles_to_excel(articles_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to Excel:\n{path}")
            self.logger.info(f"Articles exported to Excel: {path}")
        except Exception as e:
            self.logger.error(f"Export articles Excel failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export articles to Excel:\n{e}")

    def export_articles_pdf(self):
        """Export articles to PDF"""
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return
            
            # Convert Article objects to dictionaries
            articles_dict = [article.to_dict() for article in articles]
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Save Articles PDF",
                initialfile=f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            if not file_path:
                return
            
            path = self.exporter.export_articles_to_pdf(articles_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to PDF:\n{path}")
            self.logger.info(f"Articles exported to PDF: {path}")
        except Exception as e:
            self.logger.error(f"Export articles PDF failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export articles to PDF:\n{e}")

    def export_users_excel(self):
        """Export users to Excel"""
        try:
            users = self.db.get_all_users()
            if not users:
                messagebox.showinfo("Export", "No users to export")
                return
            
            # Convert User objects to dictionaries (without password hash)
            users_dict = []
            for user in users:
                user_data = user.to_dict()
                # Remove password hash for security
                user_data.pop('password_hash', None)
                users_dict.append(user_data)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Save Users Excel",
                initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            if not file_path:
                return
            
            path = self.exporter.export_users_to_excel(users_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to Excel:\n{path}")
            self.logger.info(f"Users exported to Excel: {path}")
        except Exception as e:
            self.logger.error(f"Export users Excel failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export users to Excel:\n{e}")

    def export_users_pdf(self):
        """Export users to PDF"""
        try:
            users = self.db.get_all_users()
            if not users:
                messagebox.showinfo("Export", "No users to export")
                return
            
            # Convert User objects to dictionaries (without password hash)
            users_dict = []
            for user in users:
                user_data = user.to_dict()
                user_data.pop('password_hash', None)
                users_dict.append(user_data)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Save Users PDF",
                initialfile=f"Users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            if not file_path:
                return
            
            path = self.exporter.export_users_to_pdf(users_dict, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to PDF:\n{path}")
            self.logger.info(f"Users exported to PDF: {path}")
        except Exception as e:
            self.logger.error(f"Export users PDF failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export users to PDF:\n{e}")

    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
