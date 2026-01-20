#!/usr/bin/env python3
"""
Firebase Synchronization Engine
Handles cloud data synchronization with Firestore
Author: Manoj Konar (monoj@nexuzy.in)
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False

from utils.logger import Logger
from utils.network import NetworkChecker
from utils.security import verify_password, hash_password


class FirebaseSync:
    """Manages Firebase Firestore synchronization and authentication"""

    def __init__(self):
        self.logger = Logger(__name__)
        self.db = None
        self.auth = None
        self.initialized = False
        self.network = NetworkChecker()

    def initialize(self) -> bool:
        """
        Initialize Firebase connection
        Requires firebase_config.json in project root
        
        Returns:
            bool: True if initialization successful
        """
        if not HAS_FIREBASE:
            self.logger.warning("firebase_admin not installed. Install with: pip install firebase-admin")
            return False
        
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'firebase_config.json'
            )
            
            if not os.path.exists(config_path):
                self.logger.warning(f"Firebase config not found at {config_path}")
                self.logger.info("App will work offline. Download firebase_config.json from Firebase Console.")
                return False
            
            # Initialize Firebase (prevent multiple initialization)
            if not firebase_admin._apps:
                cred = credentials.Certificate(config_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.auth = auth
            self.initialized = True
            self.logger.info("Firebase initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Firebase initialization failed: {e}")
            self.initialized = False
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with Firebase
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            dict: User data if authenticated, None otherwise
        """
        if not self.initialized or not self.network.is_connected():
            self.logger.debug("Firebase not initialized or offline")
            return None
        
        try:
            # Query Firestore for user
            docs = self.db.collection('users').where(
                'username', '==', username
            ).stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                user_data['uid'] = doc.id
                
                # Verify password if stored
                if 'password_hash' in user_data:
                    if verify_password(password, user_data['password_hash']):
                        return user_data
                
                return None
            
            return None
        
        except Exception as e:
            self.logger.error(f"Firebase authentication failed: {e}")
            return None

    def create_user(self, user_id: str, username: str, password: str, role: str = 'user') -> bool:
        """
        Create new user in Firebase
        
        Args:
            user_id: Unique user ID
            username: Username
            password: Password (will be hashed)
            role: User role (admin/user)
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            self.logger.debug("Firebase not initialized or offline")
            return False
        
        try:
            password_hash = hash_password(password)
            
            self.db.collection('users').document(user_id).set({
                'username': username,
                'password_hash': password_hash,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'id': user_id
            })
            
            self.logger.info(f"User created in Firebase: {username}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            return False

    def update_user(self, user_id: str, updates: Dict) -> bool:
        """
        Update user data in Firebase
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            return False
        
        try:
            # Remove password_hash if present (shouldn't be updated this way)
            safe_updates = {k: v for k, v in updates.items() if k != 'password_hash'}
            
            if safe_updates:
                self.db.collection('users').document(user_id).update(safe_updates)
                self.logger.info(f"User updated in Firebase: {user_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update user: {e}")
            return False

    def update_user_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            return False
        
        try:
            self.db.collection('users').document(user_id).update({
                'last_login': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            self.logger.error(f"Failed to update last login: {e}")
            return False

    def sync_articles(self, articles: List[Dict]) -> int:
        """
        Sync articles to Firebase
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            int: Number of synced articles
        """
        if not self.initialized or not self.network.is_connected():
            self.logger.debug("Cannot sync: Firebase offline")
            return 0
        
        synced = 0
        try:
            for article in articles:
                if article.get('sync_status', 0) == 0:  # Only sync pending
                    try:
                        # Prepare article data for Firebase
                        article_data = {
                            'id': article['id'],
                            'article_name': article.get('article_name', ''),
                            'mould': article.get('mould', ''),
                            'size': article.get('size', ''),
                            'gender': article.get('gender', ''),
                            'created_by': article.get('created_by', ''),
                            'created_at': article.get('created_at', datetime.now().isoformat()),
                            'updated_at': article.get('updated_at', datetime.now().isoformat())
                        }
                        
                        # Convert datetime objects to ISO format strings if needed
                        if isinstance(article_data['created_at'], datetime):
                            article_data['created_at'] = article_data['created_at'].isoformat()
                        if isinstance(article_data['updated_at'], datetime):
                            article_data['updated_at'] = article_data['updated_at'].isoformat()
                        
                        self.db.collection('articles').document(article['id']).set(
                            article_data, merge=True
                        )
                        synced += 1
                    except Exception as e:
                        self.logger.error(f"Failed to sync article {article.get('id', 'unknown')}: {e}")
            
            if synced > 0:
                self.logger.info(f"Synced {synced} articles to Firebase")
            return synced
        
        except Exception as e:
            self.logger.error(f"Article sync failed: {e}")
            return 0

    def sync_users(self, users: List[Dict]) -> int:
        """
        Sync users to Firebase (metadata only, no passwords)
        
        Args:
            users: List of user dictionaries
        
        Returns:
            int: Number of synced users
        """
        if not self.initialized or not self.network.is_connected():
            return 0
        
        synced = 0
        try:
            for user in users:
                try:
                    # Upload user metadata only
                    user_data = {
                        'username': user.get('username', ''),
                        'role': user.get('role', 'user'),
                        'created_at': user.get('created_at', datetime.now().isoformat()),
                        'last_login': user.get('last_login'),
                        'id': user['id']
                    }
                    
                    # Convert datetime to ISO string if needed
                    if isinstance(user_data['created_at'], datetime):
                        user_data['created_at'] = user_data['created_at'].isoformat()
                    if isinstance(user_data['last_login'], datetime):
                        user_data['last_login'] = user_data['last_login'].isoformat()
                    
                    # Include password_hash if present (for new users)
                    if 'password_hash' in user:
                        user_data['password_hash'] = user['password_hash']
                    
                    self.db.collection('users').document(user['id']).set(
                        user_data, merge=True
                    )
                    synced += 1
                except Exception as e:
                    self.logger.error(f"Failed to sync user {user.get('id', 'unknown')}: {e}")
            
            if synced > 0:
                self.logger.info(f"Synced {synced} users to Firebase")
            return synced
        
        except Exception as e:
            self.logger.error(f"User sync failed: {e}")
            return 0

    def get_articles_from_firebase(self) -> List[Dict]:
        """
        Download articles from Firebase
        
        Returns:
            List of article dictionaries
        """
        if not self.initialized or not self.network.is_connected():
            return []
        
        try:
            articles = []
            docs = self.db.collection('articles').stream()
            
            for doc in docs:
                article_data = doc.to_dict()
                # Ensure ID is included
                if 'id' not in article_data:
                    article_data['id'] = doc.id
                articles.append(article_data)
            
            self.logger.info(f"Downloaded {len(articles)} articles from Firebase")
            return articles
        
        except Exception as e:
            self.logger.error(f"Failed to download articles: {e}")
            return []

    def get_users_from_firebase(self) -> List[Dict]:
        """
        Download users from Firebase
        
        Returns:
            List of user dictionaries
        """
        if not self.initialized or not self.network.is_connected():
            return []
        
        try:
            users = []
            docs = self.db.collection('users').stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                # Ensure ID is included
                if 'id' not in user_data:
                    user_data['id'] = doc.id
                users.append(user_data)
            
            self.logger.info(f"Downloaded {len(users)} users from Firebase")
            return users
        
        except Exception as e:
            self.logger.error(f"Failed to download users: {e}")
            return []

    def update_article(self, article_id: str, updates: Dict) -> bool:
        """
        Update article in Firebase
        
        Args:
            article_id: Article ID
            updates: Dictionary of fields to update
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            return False
        
        try:
            # Convert datetime objects to ISO strings
            safe_updates = {}
            for key, value in updates.items():
                if isinstance(value, datetime):
                    safe_updates[key] = value.isoformat()
                else:
                    safe_updates[key] = value
            
            # Always update the updated_at timestamp
            safe_updates['updated_at'] = datetime.now().isoformat()
            
            self.db.collection('articles').document(article_id).update(safe_updates)
            self.logger.info(f"Article updated in Firebase: {article_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update article: {e}")
            return False

    def delete_article(self, article_id: str) -> bool:
        """
        Delete article from Firebase
        
        Args:
            article_id: Article ID
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            return False
        
        try:
            self.db.collection('articles').document(article_id).delete()
            self.logger.info(f"Article deleted from Firebase: {article_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete article: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user from Firebase
        
        Args:
            user_id: User ID
        
        Returns:
            bool: Success status
        """
        if not self.initialized or not self.network.is_connected():
            return False
        
        try:
            self.db.collection('users').document(user_id).delete()
            self.logger.info(f"User deleted from Firebase: {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
            return False

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """
        Get single article from Firebase by ID
        
        Args:
            article_id: Article ID
        
        Returns:
            Article dictionary or None
        """
        if not self.initialized or not self.network.is_connected():
            return None
        
        try:
            doc = self.db.collection('articles').document(article_id).get()
            if doc.exists:
                article_data = doc.to_dict()
                article_data['id'] = doc.id
                return article_data
            return None
        except Exception as e:
            self.logger.error(f"Failed to get article: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get single user from Firebase by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User dictionary or None
        """
        if not self.initialized or not self.network.is_connected():
            return None
        
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                return user_data
            return None
        except Exception as e:
            self.logger.error(f"Failed to get user: {e}")
            return None

    def batch_sync_articles(self, articles: List[Dict], batch_size: int = 500) -> int:
        """
        Sync articles in batches for better performance
        
        Args:
            articles: List of article dictionaries
            batch_size: Maximum batch size (Firestore limit is 500)
        
        Returns:
            int: Number of synced articles
        """
        if not self.initialized or not self.network.is_connected():
            return 0
        
        synced = 0
        try:
            for i in range(0, len(articles), batch_size):
                batch = self.db.batch()
                batch_articles = articles[i:i + batch_size]
                
                for article in batch_articles:
                    if article.get('sync_status', 0) == 0:
                        doc_ref = self.db.collection('articles').document(article['id'])
                        article_data = {
                            'id': article['id'],
                            'article_name': article.get('article_name', ''),
                            'mould': article.get('mould', ''),
                            'size': article.get('size', ''),
                            'gender': article.get('gender', ''),
                            'created_by': article.get('created_by', ''),
                            'created_at': article.get('created_at', datetime.now().isoformat()),
                            'updated_at': article.get('updated_at', datetime.now().isoformat())
                        }
                        
                        # Convert datetime objects
                        if isinstance(article_data['created_at'], datetime):
                            article_data['created_at'] = article_data['created_at'].isoformat()
                        if isinstance(article_data['updated_at'], datetime):
                            article_data['updated_at'] = article_data['updated_at'].isoformat()
                        
                        batch.set(doc_ref, article_data, merge=True)
                        synced += 1
                
                batch.commit()
                self.logger.debug(f"Batch synced {len(batch_articles)} articles")
            
            if synced > 0:
                self.logger.info(f"Batch synced {synced} articles to Firebase")
            return synced
        
        except Exception as e:
            self.logger.error(f"Batch sync failed: {e}")
            return synced

    def is_connected(self) -> bool:
        """
        Check if Firebase is accessible
        
        Returns:
            bool: True if Firebase initialized and internet available
        """
        return self.initialized and self.network.is_connected()

    def get_sync_status(self) -> Dict:
        """
        Get current synchronization status
        
        Returns:
            Dictionary with sync status information
        """
        return {
            'firebase_initialized': self.initialized,
            'internet_connected': self.network.is_connected(),
            'can_sync': self.is_connected(),
            'timestamp': datetime.now().isoformat()
        }
