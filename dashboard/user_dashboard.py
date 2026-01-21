#!/usr/bin/env python3
"""User Dashboard - WITH MANDATORY FTP UPLOAD

All features:
- Shows ALL articles (not just user's own)
- MANDATORY FTP upload for images
- Firebase stores ONLY FTP URLs (no local paths)
- Image preview with caching
- Article creation blocked if FTP upload fails
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os
import random
import string
from PIL import Image, ImageTk
import urllib.request
import urllib.error
import io

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

        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)

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
            self.content_frame,
            text="Quick Actions",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor=tk.W, pady=(30, 15))

        tk.Button(
            self.content_frame,
            text="+ Create New Article",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(anchor=tk.W, ipady=10, ipadx=20)

    def show_articles(self):
        self.clear_content()

        header_frame = tk.Frame(self.content_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="All Articles",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(side=tk.LEFT)

        tk.Button(
            header_frame,
            text="+ Add Article",
            font=("Arial", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(side=tk.RIGHT, ipady=6, ipadx=12)

        try:
            articles = self.db.get_all_articles()

            if articles:
                columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync", "Image")

                tree_frame = tk.Frame(self.content_frame, bg="white")
                tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

                tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")

                tree.column("ID", width=100)
                tree.column("Name", width=170)
                tree.column("Mould", width=100)
                tree.column("Size", width=80)
                tree.column("Gender", width=80)
                tree.column("Created By", width=100)
                tree.column("Date", width=100)
                tree.column("Sync", width=80)
                tree.column("Image", width=70)

                for col in columns:
                    tree.heading(col, text=col)

                for article in articles:
                    sync_status = "Synced" if article.sync_status == 1 else "Pending"
                    has_image = "✅ Yes" if article.image_path else "❌ No"
                    tree.insert("", tk.END, values=(
                        article.id[:8],
                        article.article_name,
                        article.mould,
                        article.size,
                        article.gender,
                        article.created_by[:8],
                        article.created_at.strftime("%Y-%m-%d"),
                        sync_status,
                        has_image
                    ))

                self._articles = articles
                tree.bind("<Double-1>", lambda e: self.preview_article_image(tree))

                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscroll=scrollbar.set)

                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                tk.Label(
                    self.content_frame,
                    text="💡 Tip: Double-click an article to view image (if available)",
                    font=("Arial", 9, "italic"),
                    bg="white",
                    fg="#666"
                ).pack(pady=5)
            else:
                tk.Label(
                    self.content_frame,
                    text="No articles found. Create your first article!",
                    font=("Arial", 12),
                    bg="white",
                    fg="#999"
                ).pack(pady=40)

                tk.Button(
                    self.content_frame,
                    text="+ Create First Article",
                    font=("Arial", 11),
                    bg=PRIMARY_COLOR,
                    fg="white",
                    relief=tk.FLAT,
                    cursor="hand2",
                    command=self.create_article
                ).pack(ipady=10, ipadx=20)

        except Exception as e:
            self.logger.error(f"Error loading articles: {e}")
            tk.Label(
                self.content_frame,
                text=f"Error: {e}",
                font=("Arial", 11),
                bg="white",
                fg="red"
            ).pack(pady=30)

    def preview_article_image(self, tree):
        """Preview image when article is double-clicked"""
        selection = tree.selection()
        if not selection:
            return
        
        values = tree.item(selection[0], 'values')
        article_id_short = values[0]
        
        article = None
        if hasattr(self, '_articles'):
            for a in self._articles:
                if a.id.startswith(article_id_short):
                    article = a
                    break
        
        if not article:
            messagebox.showwarning("Error", "Article not found")
            return
            
        if not article.image_path:
            messagebox.showinfo(
                "No Image", 
                f"Article: {article.article_name}\n\nNo image attached to this article."
            )
            return
        
        self.show_image_preview(article.image_path, article.article_name)

    def show_image_preview(self, image_path, title="Image Preview"):
        """Show image preview with caching support"""
        try:
            # Create preview window first
            preview = tk.Toplevel(self.root)
            preview.title(title)
            preview.geometry("700x600")
            preview.resizable(False, False)
            preview.transient(self.root)
            preview.grab_set()

            # Header
            header_frame = tk.Frame(preview, bg=PRIMARY_COLOR)
            header_frame.pack(fill=tk.X)
            tk.Label(
                header_frame,
                text=f"📷 {title}",
                font=("Arial", 12, "bold"),
                bg=PRIMARY_COLOR,
                fg="white"
            ).pack(pady=10)

            # Loading label
            loading_label = tk.Label(
                preview,
                text="Loading image...",
                font=("Arial", 11),
                fg="gray"
            )
            loading_label.pack(pady=20)

            # Image container
            image_frame = tk.Frame(preview, bg="white")
            image_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            def load_and_display():
                try:
                    img = None
                    source_label = "Loading..."

                    # Try cached image first
                    cached_path = self.image_sync.get_cached_path(image_path)
                    if cached_path and os.path.exists(cached_path):
                        self.logger.info(f"Loading from cache: {cached_path}")
                        img = Image.open(cached_path)
                        source_label = "Source: Local Cache"
                    else:
                        # Download and cache
                        if image_path.startswith(('http://', 'https://')):
                            loading_label.config(text="Downloading from FTP server...")
                            preview.update()
                            
                            cached_path = self.image_sync.download_image(image_path)
                            if cached_path and os.path.exists(cached_path):
                                img = Image.open(cached_path)
                                source_label = "Source: FTP Server (now cached)"
                            else:
                                # Fallback: direct download
                                with urllib.request.urlopen(image_path, timeout=10) as response:
                                    img_data = response.read()
                                    img = Image.open(io.BytesIO(img_data))
                                source_label = "Source: FTP Server (direct)"
                        else:
                            raise ValueError("Invalid image path (must be FTP URL)")

                    loading_label.destroy()

                    # Resize image
                    max_width = 650
                    max_height = 450
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                    # Display
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(image_frame, image=photo, bg="white")
                    img_label.image = photo
                    img_label.pack(pady=10)

                    # Info
                    info_frame = tk.Frame(preview, bg="white")
                    info_frame.pack(fill=tk.X, padx=20, pady=10)

                    tk.Label(
                        info_frame,
                        text=source_label,
                        font=("Arial", 9),
                        fg="gray"
                    ).pack()

                    tk.Label(
                        info_frame,
                        text=f"Size: {img.width}x{img.height} pixels",
                        font=("Arial", 9),
                        fg="gray"
                    ).pack()

                    if image_path.startswith(('http://', 'https://')):
                        url_label = tk.Label(
                            info_frame,
                            text=image_path,
                            font=("Arial", 8, "underline"),
                            fg="blue",
                            cursor="hand2"
                        )
                        url_label.pack()

                        def open_url(e):
                            import webbrowser
                            webbrowser.open(image_path)

                        url_label.bind("<Button-1>", open_url)

                    # Close button
                    tk.Button(
                        preview,
                        text="Close",
                        font=("Arial", 10),
                        bg="#666",
                        fg="white",
                        command=preview.destroy
                    ).pack(pady=10, ipady=5, ipadx=20)

                except Exception as e:
                    loading_label.config(text=f"Error: {str(e)}", fg="red")
                    self.logger.error(f"Error loading image: {e}")

            # Load in background
            preview.after(100, load_and_display)

        except Exception as e:
            self.logger.error(f"Error showing preview: {e}")
            messagebox.showerror("Error", f"Cannot show preview: {e}")

    def create_article(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Article")
        dialog.geometry("550x800")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        article_id = self.generate_article_id()

        header = tk.Frame(dialog, bg=PRIMARY_COLOR)
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(
            header,
            text="Create New Article",
            font=("Arial", 13, "bold"),
            bg=PRIMARY_COLOR,
            fg="white"
        ).pack(pady=15)

        id_frame = tk.Frame(dialog, bg="#f0f0f0")
        id_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        tk.Label(
            id_frame,
            text=f"Article ID: {article_id}",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg=PRIMARY_COLOR
        ).pack(pady=5)
        tk.Label(
            id_frame,
            text=f"Created by: {self.user['username']}",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=(0, 5))

        tk.Label(dialog, text="Article Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(5, 2))
        article_name_entry = tk.Entry(dialog, font=("Arial", 10), width=50)
        article_name_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Mould:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        mould_entry = tk.Entry(dialog, font=("Arial", 10), width=50)
        mould_entry.pack(padx=20, ipady=5)

        tk.Label(dialog, text="Size:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10, 2))
        size_entry = tk.Entry(dialog, font=("Arial", 10), width=50)
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

        # Image preview area
        preview_frame = tk.Frame(dialog, bg="#f0f0f0", height=120)
        preview_frame.pack(fill=tk.X, padx=20, pady=10)
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(
            preview_frame,
            text="Image preview will appear here",
            bg="#f0f0f0",
            fg="#999",
            font=("Arial", 9, "italic")
        )
        preview_label.pack(expand=True)

        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Article Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            if file_path:
                self.selected_image_path = file_path
                filename = file_path.split('/')[-1].split('\\')[-1]
                image_label.config(text=filename, fg="green")
                
                # Show preview
                try:
                    img = Image.open(file_path)
                    img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                    self.preview_photo = ImageTk.PhotoImage(img)
                    preview_label.config(image=self.preview_photo, text="")
                except Exception as e:
                    self.logger.error(f"Preview error: {e}")

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

        # Warning about FTP requirement
        warning_frame = tk.Frame(dialog, bg="#fff3cd", relief=tk.SOLID, bd=1)
        warning_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(
            warning_frame,
            text="⚠️ Images MUST be uploaded to FTP server before saving.\nArticles with images cannot be saved if FTP upload fails.",
            font=("Arial", 8),
            bg="#fff3cd",
            fg="#856404",
            justify=tk.LEFT
        ).pack(padx=10, pady=8)

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
                
                # MANDATORY FTP upload if image selected
                if self.selected_image_path:
                    status_label.config(text="⏳ Uploading image to FTP server...", fg="blue")
                    dialog.update()
                    
                    image_url = self.ftp.upload_image(self.selected_image_path)
                    
                    if not image_url:
                        status_label.config(text="❌ FTP upload failed!", fg="red")
                        dialog.update()
                        
                        result = messagebox.askyesno(
                            "FTP Upload Failed",
                            "Image could not be uploaded to FTP server.\n\n"
                            "Possible reasons:\n"
                            "• FTP credentials not configured\n"
                            "• FTP server unreachable\n"
                            "• Network connection issue\n\n"
                            "Do you want to save article WITHOUT image?"
                        )
                        
                        if not result:
                            return  # Cancel article creation
                        else:
                            image_url = None  # Save without image
                    else:
                        status_label.config(text="✅ Image uploaded to FTP!", fg="green")
                        dialog.update()

                # Create article with FTP URL ONLY (no local paths)
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
                    image_path=image_url  # FTP URL or None
                )

                if self.db.add_article(article):
                    # Sync to Firebase with FTP URL
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
        ).pack(pady=15, ipady=8, ipadx=30)

        dialog.wait_window()

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
            my_articles = self.db.get_articles_by_user(self.user['id'])
            total_count = len(my_articles)
            pending_count = len([a for a in my_articles if a.sync_status == 0])
            synced_count = total_count - pending_count

            stats_frame = tk.Frame(self.content_frame, bg="#f9f9f9", relief=tk.FLAT, bd=1)
            stats_frame.pack(fill=tk.X, pady=15, padx=10)

            tk.Label(stats_frame, text=f"My Articles: {total_count}", font=("Arial", 10), bg="#f9f9f9").pack(anchor=tk.W, padx=15, pady=5)
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
            text="User Settings",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 5))

        settings = [
            ("Username", self.user['username']),
            ("Role", self.user['role'].upper()),
            ("App Version", APP_VERSION),
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

            my_articles = self.db.get_articles_by_user(self.user['id'])
            pending_articles = [a for a in my_articles if a.sync_status == 0]

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
                my_articles = self.db.get_articles_by_user(self.user['id'])
                pending = [a for a in my_articles if a.sync_status == 0]
                if pending:
                    articles_dict = [a.to_dict() for a in pending]
                    synced = self.firebase.sync_articles(articles_dict)
                    for article in pending[:synced]:
                        self.db.mark_article_synced(article.id)
        except Exception as e:
            self.logger.debug(f"Auto-sync error: {e}")
        self.root.after(30000, self.refresh_data)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.logger.info(f"User {self.user['username']} logged out")
            self.logout_callback()
