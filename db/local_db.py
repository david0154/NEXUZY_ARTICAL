"""
Local SQLite Database Operations
Author: Manoj Konar (monoj@nexuzy.in)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging

from config import LOCAL_DB_PATH, USERS_TABLE, ARTICLES_TABLE, SYNC_PENDING, SYNC_SYNCED
from db.models import User, Article

logger = logging.getLogger(__name__)


class LocalDatabase:
    """SQLite database manager"""

    def __init__(self, db_path: Path = LOCAL_DB_PATH):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.init_database()

    # Backward-compatible alias (main.py expects initialize())
    def initialize(self):
        """Backward compatible initializer."""
        return self.init_database()

    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            # If connection already exists, don't recreate tables again
            if self.connection is None:
                self.connection = sqlite3.connect(str(self.db_path))
                self.connection.row_factory = sqlite3.Row
                self.cursor = self.connection.cursor()

            # Create users table
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    last_login DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create articles table
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {ARTICLES_TABLE} (
                    id TEXT PRIMARY KEY,
                    article_name TEXT NOT NULL,
                    mould TEXT NOT NULL,
                    size TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sync_status INTEGER DEFAULT 0,
                    FOREIGN KEY(created_by) REFERENCES {USERS_TABLE}(id)
                )
            """)

            self.connection.commit()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            logger.info("Database connection closed")

    # -----------------
    # USER OPERATIONS
    # -----------------

    def add_user(self, user: User) -> bool:
        """Add a new user"""
        try:
            self.cursor.execute(f"""
                INSERT INTO {USERS_TABLE} (id, username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user.id,
                user.username,
                user.password_hash,
                user.role,
                user.created_at or datetime.now()
            ))
            self.connection.commit()
            logger.info(f"User added: {user.username}")
            return True
        except sqlite3.IntegrityError:
            logger.error(f"User already exists: {user.username}")
            return False
        except Exception as e:
            logger.error(f"Add user failed: {e}")
            return False

    # Backward-compatible method used by login/register flows
    def create_or_update_user(self, user_id: str, username: str, password_hash: str, role: str) -> bool:
        """Create or update user by username/id."""
        try:
            self.cursor.execute(f"""
                INSERT INTO {USERS_TABLE} (id, username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username=excluded.username,
                    password_hash=excluded.password_hash,
                    role=excluded.role
            """, (user_id, username, password_hash, role, datetime.now()))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"create_or_update_user failed: {e}")
            return False

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username (returns dict for compatibility with UI code)"""
        try:
            self.cursor.execute(f"SELECT * FROM {USERS_TABLE} WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get user failed: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID (returns dict)"""
        try:
            self.cursor.execute(f"SELECT * FROM {USERS_TABLE} WHERE id = ?", (user_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None

    def get_all_users(self) -> List[User]:
        """Get all users (returns User objects)"""
        try:
            self.cursor.execute(f"SELECT * FROM {USERS_TABLE}")
            users = []
            for row in self.cursor.fetchall():
                users.append(User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role'],
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            return users
        except Exception as e:
            logger.error(f"Get all users failed: {e}")
            return []

    # Backward-compatible name used by login.py
    def update_user_last_login(self, user_id: str) -> bool:
        return self.update_last_login(user_id)

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            self.cursor.execute(f"UPDATE {USERS_TABLE} SET last_login = ? WHERE id = ?", (datetime.now(), user_id))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Update last login failed: {e}")
            return False

    # -----------------
    # ARTICLE OPERATIONS
    # -----------------

    def add_article(self, article: Article) -> bool:
        """Add a new article"""
        try:
            self.cursor.execute(f"""
                INSERT INTO {ARTICLES_TABLE} (
                    id, article_name, mould, size, gender, created_by, created_at, updated_at, sync_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.id,
                article.article_name,
                article.mould,
                article.size,
                article.gender,
                article.created_by,
                article.created_at or datetime.now(),
                article.updated_at or datetime.now(),
                SYNC_PENDING
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Add article failed: {e}")
            return False

    def get_all_articles(self) -> List[Article]:
        """Get all articles (returns Article objects)"""
        try:
            self.cursor.execute(f"SELECT * FROM {ARTICLES_TABLE} ORDER BY created_at DESC")
            articles = []
            for row in self.cursor.fetchall():
                articles.append(Article(
                    id=row['id'],
                    article_name=row['article_name'],
                    mould=row['mould'],
                    size=row['size'],
                    gender=row['gender'],
                    created_by=row['created_by'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    sync_status=row['sync_status']
                ))
            return articles
        except Exception as e:
            logger.error(f"Get all articles failed: {e}")
            return []

    def get_pending_articles(self) -> List[Article]:
        """Get articles with pending sync status"""
        try:
            self.cursor.execute(
                f"SELECT * FROM {ARTICLES_TABLE} WHERE sync_status = ? ORDER BY created_at ASC",
                (SYNC_PENDING,)
            )
            articles = []
            for row in self.cursor.fetchall():
                articles.append(Article(
                    id=row['id'],
                    article_name=row['article_name'],
                    mould=row['mould'],
                    size=row['size'],
                    gender=row['gender'],
                    created_by=row['created_by'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    sync_status=row['sync_status']
                ))
            return articles
        except Exception as e:
            logger.error(f"Get pending articles failed: {e}")
            return []

    def mark_article_synced(self, article_id: str) -> bool:
        """Mark article as synced"""
        try:
            self.cursor.execute(
                f"UPDATE {ARTICLES_TABLE} SET sync_status = ? WHERE id = ?",
                (SYNC_SYNCED, article_id)
            )
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Mark article synced failed: {e}")
            return False

    def get_articles_count(self) -> int:
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {ARTICLES_TABLE}")
            return int(self.cursor.fetchone()[0])
        except Exception as e:
            logger.error(f"Get articles count failed: {e}")
            return 0

    def get_pending_articles_count(self) -> int:
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {ARTICLES_TABLE} WHERE sync_status = ?", (SYNC_PENDING,))
            return int(self.cursor.fetchone()[0])
        except Exception as e:
            logger.error(f"Get pending articles count failed: {e}")
            return 0
