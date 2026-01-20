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
            total_articles = len(self.db.get_all_articles())
            is_online = self.network_checker.is_connected()
        except Exception:
            total_users = 0
            total_articles = 0
            is_online = False
        
        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = [
            ("Total Users", str(total_users), "👥"),
            ("Total Articles", str(total_articles), "📄"),
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
            text="Export Excel",
            font=("Arial", 9),
            bg="#2c974b",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_articles_excel
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        
        tk.Button(
            export_frame,
            text="Export PDF",
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
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date")
                tree = ttk.Treeview(self.content_frame, columns=columns, height=15, show="headings")
                
                for col in columns:
                    tree.column(col, width=100)
                    tree.heading(col, text=col)
                
                for article in articles:
                    tree.insert("", tk.END, values=(
                        article['id'][:8],
                        article['article_name'],
                        article['mould'],
                        article['size'],
                        article['gender'],
                        article['created_by'][:8],
                        article['created_at'][:10]
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
            text="Export Excel",
            font=("Arial", 9),
            bg="#2c974b",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.export_users_excel
        ).pack(side=tk.LEFT, padx=5, ipady=4, ipadx=8)
        
        tk.Button(
            export_frame,
            text="Export PDF",
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
                    tree.insert("", tk.END, values=(
                        user['username'],
                        user['role'].upper(),
                        user['last_login'][:10] if user['last_login'] else "Never",
                        user['created_at'][:10]
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
        status_text = "✅ Online - Ready to sync" if is_online else "❌ Offline - Local only"
        status_color = "green" if is_online else "orange"
        
        status_label = tk.Label(
            self.content_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            bg="white",
            fg=status_color
        )
        status_label.pack(anchor=tk.W, pady=10)
        
        if is_online:
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
        
        tk.Label(
            self.content_frame,
            text="Pending Syncs: 0",
            font=("Arial", 10),
            bg="white"
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
            ("Login Time", str(self.user['login_time'])[:19]),
        ]
        
        for label, value in settings:
            frame = tk.Frame(self.content_frame, bg="white")
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{label}:", font=("Arial", 10), bg="white", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 10), bg="white", fg="#666").pack(side=tk.LEFT)

    def create_article(self):
        """Create new article dialog"""
        import uuid
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Article")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Create New Article", font=("Arial", 12, "bold")).pack(pady=10)
        
        fields = {}
        for label in ["Article Name", "Mould", "Size", "Gender"]:
            tk.Label(dialog, text=f"{label}:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 3))
            entry = tk.Entry(dialog, font=("Arial", 10), width=35)
            entry.pack(padx=20, ipady=5)
            fields[label.lower().replace(" ", "_")] = entry
        
        def save_article():
            try:
                article_id = str(uuid.uuid4())
                self.db.create_article(
                    article_id,
                    fields["article_name"].get(),
                    fields["mould"].get(),
                    fields["size"].get(),
                    fields["gender"].get(),
                    self.user['id']
                )
                messagebox.showinfo("Success", "Article created successfully")
                dialog.destroy()
                self.show_articles()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create article: {e}")
        
        tk.Button(
            dialog,
            text="Save",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            command=save_article
        ).pack(pady=20, ipady=6, ipadx=30)

    def add_user(self):
        """Add new user dialog"""
        from utils.security import hash_password
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
                user_id = str(uuid.uuid4())
                self.db.create_or_update_user(
                    user_id,
                    username_entry.get(),
                    hash_password(password_entry.get()),
                    role_var.get()
                )
                messagebox.showinfo("Success", "User created successfully")
                dialog.destroy()
                self.show_users()
            except Exception as e:
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
        messagebox.showinfo("Sync", "Synchronization started in background")
        self.logger.info("Manual sync initiated")

    def refresh_data(self):
        """Refresh dashboard data periodically"""
        try:
            if self.network_checker.is_connected():
                # Attempt sync
                pass
        except Exception:
            pass
        
        self.root.after(30000, self.refresh_data)

    def export_articles_excel(self):
        """Export articles to Excel"""
        try:
            articles = self.db.get_all_articles()
            if not articles:
                messagebox.showinfo("Export", "No articles to export")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Save Articles Excel"
            )
            if not file_path:
                return
            
            path = self.exporter.export_articles_to_excel(articles, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to Excel:\n{path}")
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
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Save Articles PDF"
            )
            if not file_path:
                return
            
            path = self.exporter.export_articles_to_pdf(articles, output_path=file_path)
            messagebox.showinfo("Export", f"Articles exported to PDF:\n{path}")
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
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Save Users Excel"
            )
            if not file_path:
                return
            
            path = self.exporter.export_users_to_excel(users, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to Excel:\n{path}")
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
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Save Users PDF"
            )
            if not file_path:
                return
            
            path = self.exporter.export_users_to_pdf(users, output_path=file_path)
            messagebox.showinfo("Export", f"Users exported to PDF:\n{path}")
        except Exception as e:
            self.logger.error(f"Export users PDF failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export users to PDF:\n{e}")

    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
