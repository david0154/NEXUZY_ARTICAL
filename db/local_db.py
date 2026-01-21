# Add these methods to LocalDatabase class:

    def delete_user(self, user_id):
        """Delete user from database"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
            self.logger.info(f"User deleted: {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Delete user failed: {e}")
            return False

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, password_hash, role, created_at, last_login FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'password_hash': row[2],
                        'role': row[3],
                        'created_at': row[4],
                        'last_login': row[5]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Get user by ID failed: {e}")
            return None
