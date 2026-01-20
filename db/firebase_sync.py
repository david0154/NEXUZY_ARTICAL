"""
Firebase Synchronization Engine
Author: Manoj Konar (monoj@nexuzy.in)
"""

import logging
from typing import List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CONFIG_PATH, SYNC_SYNCED
from db.models import Article, User
from utils.network import is_online

logger = logging.getLogger(__name__)

class FirebaseSync:
    """Firebase Firestore synchronization manager"""
    
    def __init__(self):
        self.db = None
        self.initialized = False
        self.init_firebase()
    
    def init_firebase(self) -> bool:
        """Initialize Firebase connection"""
        try:
            if not FIREBASE_CONFIG_PATH.exists():
                logger.error(f"Firebase config not found: {FIREBASE_CONFIG_PATH}")
                logger.info("App will work offline. Create firebase_config.json to enable sync.")
                return False
            
            # Initialize Firebase (only if not already initialized)
            if not firebase_admin._apps:
                cred = credentials.Certificate(str(FIREBASE_CONFIG_PATH))
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.initialized = True
            logger.info("Firebase initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            self.initialized = False
            return False
    
    def sync_articles(self, pending_articles: List[Article]) -> int:
        """
        Sync pending articles to Firebase
        
        Args:
            pending_articles: List of articles with sync_status = 0
            
        Returns:
            int: Number of successfully synced articles
        """
        if not self.initialized or not is_online():
            logger.warning("Cannot sync: Firebase not initialized or no internet")
            return 0
        
        synced_count = 0
        try:
            for article in pending_articles:
                try:
                    # Upload to Firebase
                    self.db.collection('articles').document(article.id).set(
                        article.to_firebase_dict()
                    )
                    synced_count += 1
                    logger.info(f"Article synced: {article.id}")
                except Exception as e:
                    logger.error(f"Failed to sync article {article.id}: {e}")
                    continue
            
            logger.info(f"Sync completed: {synced_count}/{len(pending_articles)} articles")
            return synced_count
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            return 0
    
    def sync_users(self, users: List[User]) -> int:
        """
        Sync users to Firebase
        
        Args:
            users: List of users
            
        Returns:
            int: Number of successfully synced users
        """
        if not self.initialized or not is_online():
            logger.warning("Cannot sync: Firebase not initialized or no internet")
            return 0
        
        synced_count = 0
        try:
            for user in users:
                try:
                    self.db.collection('users').document(user.id).set({
                        'username': user.username,
                        'role': user.role,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    }, merge=True)
                    synced_count += 1
                    logger.info(f"User synced: {user.username}")
                except Exception as e:
                    logger.error(f"Failed to sync user {user.username}: {e}")
                    continue
            
            logger.info(f"User sync completed: {synced_count}/{len(users)} users")
            return synced_count
        except Exception as e:
            logger.error(f"User sync failed: {e}")
            return 0
    
    def download_articles(self) -> List[Article]:
        """
        Download latest articles from Firebase
        
        Returns:
            List of Article objects from Firebase
        """
        if not self.initialized or not is_online():
            logger.warning("Cannot download: Firebase not initialized or no internet")
            return []
        
        try:
            articles = []
            docs = self.db.collection('articles').stream()
            
            for doc in docs:
                data = doc.to_dict()
                article = Article(
                    id=doc.id,
                    article_name=data.get('article_name', ''),
                    mould=data.get('mould', ''),
                    size=data.get('size', ''),
                    gender=data.get('gender', ''),
                    created_by=data.get('created_by', ''),
                    created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
                    sync_status=SYNC_SYNCED
                )
                articles.append(article)
            
            logger.info(f"Downloaded {len(articles)} articles from Firebase")
            return articles
        except Exception as e:
            logger.error(f"Download articles failed: {e}")
            return []
    
    def download_users(self) -> List[User]:
        """
        Download latest users from Firebase
        
        Returns:
            List of User objects from Firebase
        """
        if not self.initialized or not is_online():
            logger.warning("Cannot download: Firebase not initialized or no internet")
            return []
        
        try:
            users = []
            docs = self.db.collection('users').stream()
            
            for doc in docs:
                data = doc.to_dict()
                user = User(
                    id=doc.id,
                    username=data.get('username', ''),
                    password_hash='',  # Don't store password from cloud
                    role=data.get('role', 'user'),
                    created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
                )
                users.append(user)
            
            logger.info(f"Downloaded {len(users)} users from Firebase")
            return users
        except Exception as e:
            logger.error(f"Download users failed: {e}")
            return []
    
    def delete_article(self, article_id: str) -> bool:
        """
        Delete article from Firebase
        
        Args:
            article_id: Article ID to delete
            
        Returns:
            bool: Success status
        """
        if not self.initialized or not is_online():
            logger.warning("Cannot delete: Firebase not initialized or no internet")
            return False
        
        try:
            self.db.collection('articles').document(article_id).delete()
            logger.info(f"Article deleted from Firebase: {article_id}")
            return True
        except Exception as e:
            logger.error(f"Delete article failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Firebase is accessible"""
        return self.initialized and is_online()
