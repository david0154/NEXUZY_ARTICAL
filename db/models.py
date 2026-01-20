"""
Data models for NEXUZY ARTICAL
Author: Manoj Konar (monoj@nexuzy.in)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model"""
    id: str
    username: str
    password_hash: str
    role: str  # 'admin' or 'user'
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def is_admin(self) -> bool:
        return self.role.lower() == 'admin'
    
    def is_user(self) -> bool:
        return self.role.lower() == 'user'
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Article:
    """Article model"""
    id: str
    article_name: str
    mould: str
    size: str
    gender: str
    created_by: str  # User ID
    created_at: datetime
    updated_at: Optional[datetime] = None
    sync_status: int = 0  # 0 = pending, 1 = synced
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'article_name': self.article_name,
            'mould': self.mould,
            'size': self.size,
            'gender': self.gender,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sync_status': self.sync_status
        }
    
    def to_firebase_dict(self) -> dict:
        """Convert to Firebase format (without sync_status)"""
        return {
            'article_name': self.article_name,
            'mould': self.mould,
            'size': self.size,
            'gender': self.gender,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
