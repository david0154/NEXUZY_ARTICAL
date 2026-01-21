#!/usr/bin/env python3
"""Enhanced Firebase Sync Module

Features:
- Bidirectional sync (upload AND download)
- Fresh install: Download all Firebase data to local DB
- Delete sync: Delete from Firebase when deleted locally
- Auto-sync on startup

Author: Manoj Konar (monoj@nexuzy.in)

Build-safe config:
- Uses config.FIREBASE_CONFIG_PATH (writable app-data folder Option B)
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config import FIREBASE_CONFIG_PATH

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase not installed. Running in offline mode.")

logger = logging.getLogger(__name__)


class FirebaseSync:
    """Handles all Firebase Firestore operations with bidirectional sync"""

    def __init__(self, config_path: str = None):
        # Default to build-safe runtime location
        self.config_path = str(FIREBASE_CONFIG_PATH) if config_path is None else config_path
        self.db = None
        self.initialized = False
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase connection"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase SDK not available")
            return

        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.warning(f"Firebase config not found: {self.config_path}")
                return

            if not firebase_admin._apps:
                cred = credentials.Certificate(str(config_file))
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            self.initialized = True
            logger.info("Firebase initialized successfully")

        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            self.initialized = False

    def is_connected(self) -> bool:
        return self.initialized and self.db is not None

    def download_all_articles(self) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            articles_ref = self.db.collection("articles")
            docs = articles_ref.stream()
            articles = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                articles.append(data)
            logger.info(f"Downloaded {len(articles)} articles from Firebase")
            return articles
        except Exception as e:
            logger.error(f"Failed to download articles from Firebase: {e}")
            return []

    def upload_article(self, article_dict: Dict) -> bool:
        if not self.is_connected():
            return False
        try:
            article_id = article_dict.get("id")
            if not article_id:
                logger.error("Article ID missing")
                return False
            self.db.collection("articles").document(article_id).set(article_dict)
            logger.info(f"Uploaded article {article_id} to Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to upload article: {e}")
            return False

    def sync_articles(self, articles: List[Dict]) -> int:
        if not self.is_connected():
            return 0
        count = 0
        for article in articles:
            if self.upload_article(article):
                count += 1
        return count

    def update_article(self, article_id: str, updates: Dict) -> bool:
        if not self.is_connected():
            return False
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.db.collection("articles").document(article_id).update(updates)
            logger.info(f"Updated article {article_id} in Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to update article in Firebase: {e}")
            return False

    def delete_article(self, article_id: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.db.collection("articles").document(article_id).delete()
            logger.info(f"Deleted article {article_id} from Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to delete article {article_id} from Firebase: {e}")
            return False

    def download_all_users(self) -> List[Dict]:
        if not self.is_connected():
            return []
        try:
            users_ref = self.db.collection("users")
            docs = users_ref.stream()
            users = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                users.append(data)
            logger.info(f"Downloaded {len(users)} users from Firebase")
            return users
        except Exception as e:
            logger.error(f"Failed to download users from Firebase: {e}")
            return []

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        if not self.is_connected():
            return None
        try:
            users_ref = self.db.collection("users")
            query = users_ref.where("username", "==", username).limit(1)
            docs = list(query.stream())
            if not docs:
                return None
            user_data = docs[0].to_dict()
            user_data["uid"] = docs[0].id
            return user_data
        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            return None

    def delete_user(self, user_id: str) -> bool:
        if not self.is_connected():
            return False
        try:
            self.db.collection("users").document(user_id).delete()
            logger.info(f"Deleted user {user_id} from Firebase")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id} from Firebase: {e}")
            return False

    def initial_sync_from_firebase(self, local_db) -> Dict[str, int]:
        stats = {"articles": 0, "users": 0, "errors": 0}
        if not self.is_connected():
            logger.warning("Cannot sync: Firebase not connected")
            return stats
        try:
            local_article_count = local_db.get_articles_count()
            local_user_count = len(local_db.get_all_users())

            firebase_articles = self.download_all_articles()
            if firebase_articles and len(firebase_articles) > local_article_count:
                from db.models import Article
                for article_dict in firebase_articles:
                    try:
                        article = Article(
                            id=article_dict.get("id"),
                            article_name=article_dict.get("article_name"),
                            mould=article_dict.get("mould"),
                            size=article_dict.get("size"),
                            gender=article_dict.get("gender"),
                            created_by=article_dict.get("created_by"),
                            created_at=datetime.fromisoformat(article_dict.get("created_at"))
                            if article_dict.get("created_at")
                            else datetime.now(),
                            updated_at=datetime.fromisoformat(article_dict.get("updated_at"))
                            if article_dict.get("updated_at")
                            else None,
                            sync_status=1,
                            image_path=article_dict.get("image_path"),
                        )
                        if local_db.add_article(article):
                            stats["articles"] += 1
                    except Exception as e:
                        logger.error(f"Failed to import article: {e}")
                        stats["errors"] += 1

            firebase_users = self.download_all_users()
            if firebase_users and len(firebase_users) > local_user_count:
                from db.models import User
                for user_dict in firebase_users:
                    try:
                        user = User(
                            id=user_dict.get("id"),
                            username=user_dict.get("username"),
                            password_hash=user_dict.get("password_hash"),
                            role=user_dict.get("role", "user"),
                            created_at=datetime.fromisoformat(user_dict.get("created_at"))
                            if user_dict.get("created_at")
                            else datetime.now(),
                            last_login=None,
                        )
                        if local_db.add_user(user):
                            stats["users"] += 1
                    except Exception as e:
                        logger.error(f"Failed to import user: {e}")
                        stats["errors"] += 1

            logger.info(
                f"Firebase import complete: {stats['articles']} articles, {stats['users']} users"
            )
            return stats
        except Exception as e:
            logger.error(f"Initial sync from Firebase failed: {e}")
            stats["errors"] += 1
            return stats
