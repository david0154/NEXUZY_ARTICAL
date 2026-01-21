# Code Snippets for Dashboard Updates

This file contains the exact code snippets to add search, double-click details, and image preview features to your dashboards.

---

## 1. Required Imports

Add these imports at the top of both `admin_dashboard.py` and `user_dashboard.py`:

```python
from PIL import Image, ImageTk
import requests
from io import BytesIO
```

---

## 2. Initialize Search Variables

In the `__init__` method, add:

```python
def __init__(self, root, user, db, firebase, network_checker, logout_callback, logger):
    # ... existing code ...
    self.ftp = get_ftp_uploader()
    self.selected_image_path = None
    
    # ADD THESE LINES:
    self.all_articles = []  # Cache for search
    self.search_var = tk.StringVar()
    self._article_id_map = {}  # Map short IDs to full IDs
```

---

## 3. Add Search Box to Articles View

In the `show_articles()` method, add search box before the treeview:

```python
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
    
    # ADD SEARCH BOX:
    search_frame = tk.Frame(header_frame, bg="white")
    search_frame.pack(side=tk.LEFT, padx=20)
    
    tk.Label(
        search_frame, 
        text="🔍", 
        font=("Arial", 14), 
        bg="white"
    ).pack(side=tk.LEFT)
    
    search_entry = tk.Entry(
        search_frame, 
        textvariable=self.search_var,
        font=("Arial", 10), 
        width=30
    )
    search_entry.pack(side=tk.LEFT, padx=5, ipady=4)
    search_entry.bind('<KeyRelease>', self.search_articles)
    
    tk.Label(
        search_frame,
        text="Search by name or mould",
        font=("Arial", 8),
        fg="gray",
        bg="white"
    ).pack(side=tk.LEFT, padx=5)
    
    # ... rest of the method ...
```

---

## 4. Load All Articles into Cache

Modify the articles loading section in `show_articles()`:

```python
try:
    # Load articles and cache them
    self.all_articles = self.db.get_all_articles()
    self._article_id_map = {}
    
    if self.all_articles:
        columns = ("ID", "Name", "Mould", "Size", "Gender", "Created By", "Date", "Sync")
        
        tree_frame = tk.Frame(self.content_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.articles_tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")
        
        # Set column widths
        self.articles_tree.column("ID", width=100)
        self.articles_tree.column("Name", width=200)
        # ... other columns ...
        
        # Set headings
        for col in columns:
            self.articles_tree.heading(col, text=col)
        
        # Populate tree
        for article in self.all_articles:
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
        
        # ADD DOUBLE-CLICK BINDING:
        self.articles_tree.bind("<Double-1>", self.show_article_details)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.articles_tree.yview)
        self.articles_tree.configure(yscroll=scrollbar.set)
        
        self.articles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
```

---

## 5. Add Search Method

Add this new method to the dashboard class:

```python
def search_articles(self, event=None):
    """Filter articles based on search query"""
    query = self.search_var.get().lower().strip()
    
    # Clear existing items
    for item in self.articles_tree.get_children():
        self.articles_tree.delete(item)
    
    # If no query, show all
    if not query:
        articles_to_show = self.all_articles
    else:
        # Filter articles
        articles_to_show = [
            article for article in self.all_articles
            if query in article.article_name.lower() or 
               query in article.mould.lower()
        ]
    
    # Populate tree with filtered results
    for article in articles_to_show:
        short_id = article.id[:8]
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
```

---

## 6. Add Article Details Dialog Method

Add this new method to show article details on double-click:

```python
def show_article_details(self, event):
    """Show detailed article information on double-click"""
    selection = self.articles_tree.selection()
    if not selection:
        return
    
    values = self.articles_tree.item(selection[0], "values")
    if not values:
        return
    
    short_id = values[0]
    article_id = self._article_id_map.get(short_id)
    if not article_id:
        return
    
    article = self.db.get_article_by_id(article_id)
    if not article:
        messagebox.showerror("Error", "Article not found")
        return
    
    # Create details dialog
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Article Details - {article.article_name}")
    dialog.geometry("600x700")
    dialog.resizable(False, False)
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Header
    header = tk.Frame(dialog, bg=PRIMARY_COLOR)
    header.pack(fill=tk.X, pady=(0, 15))
    tk.Label(
        header,
        text=f"📋 {article.article_name}",
        font=("Arial", 14, "bold"),
        bg=PRIMARY_COLOR,
        fg="white"
    ).pack(pady=15)
    
    # Scrollable content
    canvas = tk.Canvas(dialog, bg="white")
    scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Article details
    details = [
        ("Article ID", article.id),
        ("Article Name", article.article_name),
        ("Mould", article.mould),
        ("Size", article.size),
        ("Gender", article.gender),
        ("Created By", article.created_by[:8]),
        ("Created At", article.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        ("Updated At", article.updated_at.strftime("%Y-%m-%d %H:%M:%S")),
        ("Sync Status", "Synced" if article.sync_status == 1 else "Pending"),
    ]
    
    for label, value in details:
        row = tk.Frame(scrollable_frame, bg="white")
        row.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(
            row,
            text=f"{label}:",
            font=("Arial", 10, "bold"),
            bg="white",
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=value,
            font=("Arial", 10),
            bg="white",
            fg="#333",
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Image section
    if article.image_path:
        tk.Label(
            scrollable_frame,
            text="Image:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        image_frame = tk.Frame(scrollable_frame, bg="white", relief=tk.SOLID, bd=1)
        image_frame.pack(padx=20, pady=5, fill=tk.X)
        
        # Load image from URL
        self.load_image_from_url(article.image_path, image_frame)
    else:
        tk.Label(
            scrollable_frame,
            text="🖼️ No image available",
            font=("Arial", 10),
            bg="white",
            fg="gray"
        ).pack(pady=20)
    
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    # Close button
    tk.Button(
        dialog,
        text="Close",
        font=("Arial", 10),
        bg="#666",
        fg="white",
        command=dialog.destroy
    ).pack(pady=10, ipady=6, ipadx=30)
    
    dialog.wait_window()
```

---

## 7. Add Image Loading Method

Add this method to load images from URLs:

```python
def load_image_from_url(self, url, parent_widget):
    """Load and display image from URL"""
    try:
        # Show loading message
        loading_label = tk.Label(
            parent_widget,
            text="⏳ Loading image...",
            font=("Arial", 9),
            fg="blue",
            bg="white"
        )
        loading_label.pack(pady=10)
        parent_widget.update()
        
        # Download image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Open image
        image_data = Image.open(BytesIO(response.content))
        
        # Resize to fit (max 400x400)
        image_data.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image_data)
        
        # Remove loading message
        loading_label.destroy()
        
        # Display image
        image_label = tk.Label(parent_widget, image=photo, bg="white")
        image_label.image = photo  # Keep reference to prevent garbage collection
        image_label.pack(pady=10)
        
        # Add image info
        tk.Label(
            parent_widget,
            text=f"Size: {image_data.width}x{image_data.height}px",
            font=("Arial", 8),
            fg="gray",
            bg="white"
        ).pack(pady=2)
        
    except requests.RequestException as e:
        loading_label.destroy()
        tk.Label(
            parent_widget,
            text=f"⚠️ Cannot load image\n{str(e)[:50]}",
            font=("Arial", 9),
            fg="orange",
            bg="white"
        ).pack(pady=10)
        
    except Exception as e:
        loading_label.destroy()
        tk.Label(
            parent_widget,
            text=f"❌ Image error\n{str(e)[:50]}",
            font=("Arial", 9),
            fg="red",
            bg="white"
        ).pack(pady=10)
```

---

## 8. Update Image Upload in Create/Edit Article

In the `create_article()` method's `save_article()` function:

```python
def save_article():
    try:
        # ... get article data ...
        
        image_url = None
        if self.selected_image_path:
            # Show uploading status
            status_label.config(text="⏳ Uploading image to FTP...", fg="blue")
            dialog.update()
            
            # Upload to FTP server
            image_url = self.ftp.upload_image(self.selected_image_path)
            
            if image_url:
                status_label.config(text=f"✅ Image uploaded!\n{image_url}", fg="green")
            else:
                status_label.config(text="⚠️ FTP upload failed", fg="orange")
            
            dialog.update()
        
        # Create article with image URL
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
            image_path=image_url  # Store FTP URL
        )
        
        # Save to local database
        if self.db.add_article(article):
            # Sync to Firebase (includes image URL)
            if self.firebase and self.firebase.is_connected():
                synced = self.firebase.sync_articles([article.to_dict()])
                if synced:
                    self.db.mark_article_synced(article.id)
            
            messagebox.showinfo("Success", 
                f"Article created!\nID: {article_id}" +
                (f"\nImage: {image_url}" if image_url else ""))
            
            dialog.destroy()
            self.selected_image_path = None
            self.show_articles()
        else:
            messagebox.showerror("Error", "Failed to create article")
    
    except Exception as e:
        self.logger.error(f"Error creating article: {e}")
        messagebox.showerror("Error", f"Failed: {e}")
```

---

## 9. Install Dependencies

Run these commands:

```bash
pip install pillow requests
```

Or add to `requirements.txt`:

```
pillow>=10.0.0
requests>=2.31.0
```

---

## 10. Setup FTP Configuration

Create `ftp_config.json` in project root:

```json
{
  "ftp_host": "ftp.yourdomain.com",
  "ftp_user": "your_username",
  "ftp_pass": "your_password",
  "ftp_remote_dir": "/public_html/articles/images",
  "ftp_base_url": "https://yourdomain.com/articles/images"
}
```

---

## Testing

### Test Search:
1. Open Articles view
2. Type in search box
3. Results should filter in real-time
4. Clear box to show all

### Test Double-Click:
1. Double-click any article
2. Details dialog should open
3. All information should display
4. Image should load (if URL exists)

### Test FTP Upload:
1. Create new article
2. Select an image
3. Save article
4. Check status shows upload progress
5. Verify image URL is saved
6. Double-click article to view image

---

**Implementation Note**: Apply these snippets to BOTH `admin_dashboard.py` AND `user_dashboard.py` for consistent functionality across both interfaces.

---

**Last Updated**: January 21, 2026