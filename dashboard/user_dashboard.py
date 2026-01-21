#!/usr/bin/env python3
"""User Dashboard Module - FIXED WINDOW SIZING
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
from utils.ftp_uploader import get_ftp_uploader


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
        self.selected_image_path = None

        self.root.deiconify()
        self.setup_ui()
        self.refresh_data()
        self.logger.info(f"User dashboard initialized: {user['username']}")

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
        """Setup UI - FIXED SIZING"""
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
            ("📄 My Articles", self.show_my_articles),
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

        # CRITICAL FIX: Content frame directly without canvas
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
            text="Dashboard",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 20))

        tk.Button(
            self.content_frame,
            text="+ Create New Article",
            font=("Arial", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.create_article
        ).pack(fill=tk.X, pady=5, ipady=10)

    def show_my_articles(self):
        self.clear_content()
        tk.Label(
            self.content_frame,
            text="My Articles",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 20))

    def create_article(self):
        """Create article dialog"""
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

        image_frame = tk.Frame(dialog)
        image_frame.pack(pady=15, padx=20, fill=tk.X)
        
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
                if not all([article_name_entry.get().strip(), mould_entry.get().strip(), 
                           size_entry.get().strip()]):
                    messagebox.showerror("Error", "Please fill all fields")
                    return
                
                image_url = None
                if self.selected_image_path:
                    status_label.config(text="⏳ Uploading image...", fg="blue")
                    dialog.update()
                    image_url = self.ftp.upload_image(self.selected_image_path)
                    if image_url:
                        status_label.config(text="✅ Image uploaded!", fg="green")
                    dialog.update()
                
                self.db.create_article(
                    article_id,
                    article_name_entry.get().strip(),
                    mould_entry.get().strip(),
                    size_entry.get().strip(),
                    gender_var.get(),
                    self.user['id'],
                    image_url
                )
                
                messagebox.showinfo("Success", f"Article created!\nID: {article_id}")
                dialog.destroy()
                self.selected_image_path = None
                self.show_my_articles()
            except Exception as e:
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

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.logout_callback()

    def refresh_data(self):
        pass
