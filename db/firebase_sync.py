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
                        self.db.collection('articles').document(article['id']).set({
                            'id': article['id'],
                            'article_name': article.get('article_name', ''),
                            'mould': article.get('mould', ''),
                            'size': article.get('size', ''),
                            'gender': article.get('gender', ''),
                            'created_by': article.get('created_by', ''),
                            'created_at': article.get('created_at', datetime.now().isoformat()),
                            'updated_at': article.get('updated_at', datetime.now().isoformat()),
                            'sync_status': 1
                        }, merge=True)
                        synced += 1
                    except Exception as e:
                        self.logger.error(f"Failed to sync article {article['id']}: {e}")
            
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
                    # Upload user metadata only (no password)
                    self.db.collection('users').document(user['id']).set({
                        'username': user.get('username', ''),
                        'role': user.get('role', 'user'),
                        'created_at': user.get('created_at', datetime.now().isoformat()),
                        'last_login': user.get('last_login'),
                        'id': user['id']
                    }, merge=True)
                    synced += 1
                except Exception as e:
                    self.logger.error(f"Failed to sync user {user['id']}: {e}")
            
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
                articles.append(doc.to_dict())
            
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
                users.append(doc.to_dict())
            
            self.logger.info(f"Downloaded {len(users)} users from Firebase")
            return users
        
        except Exception as e:
            self.logger.error(f"Failed to download users: {e}")
            return []

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

    def is_connected(self) -> bool:
        """
        Check if Firebase is accessible
        
        Returns:
            bool: True if Firebase initialized and internet available
        """
        return self.initialized and self.network.is_connected()
