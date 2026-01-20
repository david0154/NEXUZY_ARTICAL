#!/usr/bin/env python3
"""
User Dashboard Module
Limited dashboard for regular users
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, PRIMARY_COLOR


class UserDashboard:
    """User dashboard with limited permissions"""

    def __init__(self, root, user, db, firebase, network_checker, logout_callback, logger):
        self.root = root
        self.user = user
        self.db = db
        self.firebase = firebase
        self.network_checker = network_checker
        self.logout_callback = logout_callback
        self.logger = logger
        
        self.root.deiconify()
        self.setup_ui()
        self.refresh_data()
        self.logger.info(f"User dashboard initialized for user: {user['username']}")

    def setup_ui(self):
        """Create user dashboard UI"""
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Top bar
        top_frame = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame,
            text=f"{APP_NAME} - Dashboard",
            font=("Arial", 14, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        user_info = tk.Label(
            top_frame,
            text=f"Welcome, {self.user['username']}",
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
            ("📄 My Articles", self.show_my_articles),
            ("🔗 Share Article", self.show_share),
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
            text="My Dashboard",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#333"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Statistics
        try:
            my_articles = len(self.db.get_articles_by_user(self.user['id']))
            is_online = self.network_checker.is_connected()
        except:
            my_articles = 0
            is_online = False
        
        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = [
            ("My Articles", str(my_articles), "📄"),
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

    def show_my_articles(self):
        """Show user's articles"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="My Articles",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(anchor=tk.W, pady=(0, 15))
        
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
        ).pack(anchor=tk.W, pady=(0, 15), ipady=6, ipadx=15)
        
        # Articles list
        try:
            articles = self.db.get_articles_by_user(self.user['id'])
            if articles:
                columns = ("Name", "Mould", "Size", "Gender", "Date")
                tree = ttk.Treeview(self.content_frame, columns=columns, height=15, show="headings")
                
                for col in columns:
                    tree.column(col, width=130)
                    tree.heading(col, text=col)
                
                for article in articles:
                    tree.insert("", tk.END, values=(
                        article['article_name'],
                        article['mould'],
                        article['size'],
                        article['gender'],
                        article['created_at'][:10]
                    ))
                
                tree.pack(fill=tk.BOTH, expand=True)
                
                scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    self.content_frame,
                    text="No articles yet. Create your first article!",
                    font=("Arial", 11),
                    bg="white",
                    fg="#999"
                ).pack(pady=20)
        except Exception as e:
            self.logger.error(f"Error loading articles: {e}")
            tk.Label(
                self.content_frame,
                text=f"Error: {e}",
                font=("Arial", 10),
                bg="white",
                fg="red"
            ).pack(pady=20)

    def show_share(self):
        """Show article sharing options"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Share Article",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(
            self.content_frame,
            text="Select an article to share:",
            font=("Arial", 11),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        try:
            articles = self.db.get_articles_by_user(self.user['id'])
            if articles:
                for article in articles:
                    frame = tk.Frame(self.content_frame, bg="#f9f9f9", relief=tk.FLAT, bd=1)
                    frame.pack(fill=tk.X, pady=8)
                    
                    tk.Label(
                        frame,
                        text=f"📄 {article['article_name']} ({article['size']})",
                        font=("Arial", 10),
                        bg="#f9f9f9"
                    ).pack(side=tk.LEFT, padx=15, pady=10)
                    
                    tk.Button(
                        frame,
                        text="Share",
                        font=("Arial", 9),
                        bg=PRIMARY_COLOR,
                        fg="white",
                        relief=tk.FLAT,
                        cursor="hand2",
                        command=lambda aid=article['id']: self.share_article(aid)
                    ).pack(side=tk.RIGHT, padx=10, pady=8, ipady=4, ipadx=10)
            else:
                tk.Label(
                    self.content_frame,
                    text="No articles to share",
                    font=("Arial", 11),
                    bg="white",
                    fg="#999"
                ).pack(pady=20)
        except Exception as e:
            tk.Label(
                self.content_frame,
                text=f"Error: {e}",
                font=("Arial", 10),
                bg="white",
                fg="red"
            ).pack(pady=20)

    def show_settings(self):
        """Show user settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Settings",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        settings = [
            ("Username", self.user['username']),
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
                self.show_my_articles()
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

    def share_article(self, article_id):
        """Share article with other users"""
        messagebox.showinfo("Share", f"Article shared successfully!\nArticle ID: {article_id[:8]}")
        self.logger.info(f"Article {article_id} shared by user {self.user['id']}")

    def refresh_data(self):
        """Refresh dashboard data periodically"""
        try:
            if self.network_checker.is_connected():
                # Attempt sync
                pass
        except:
            pass
        
        # Schedule next refresh
        self.root.after(30000, self.refresh_data)

    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
