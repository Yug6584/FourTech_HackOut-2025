# database_utils.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        # Get configuration from environment variables directly
        self.host = os.environ.get('MYSQL_HOST', 'localhost')
        self.user = os.environ.get('MYSQL_USER', 'root')
        self.password = os.environ.get('MYSQL_PASSWORD', '!S6L^0r&06*a')
        self.database = os.environ.get('MYSQL_DB', 'terragen')
    
    def get_connection(self):
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False  # Explicitly manage transactions
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def save_chat_session(self, session_data):
        """Save or update a chat session"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            cursor = connection.cursor()
            
            if 'session_id' in session_data and session_data['session_id']:
                # Update existing session
                query = """
                    UPDATE chat_sessions 
                    SET location = %s, latitude = %s, longitude = %s, 
                        feasibility_score = %s, recommended_technology = %s,
                        updated_at = %s
                    WHERE id = %s
                """
                values = (
                    session_data.get('location', 'Unknown'),
                    session_data.get('latitude'),
                    session_data.get('longitude'),
                    session_data.get('feasibility'),
                    session_data.get('recommended_technology'),
                    datetime.now(),
                    session_data['session_id']
                )
                cursor.execute(query, values)
                session_id = session_data['session_id']
            else:
                # Create new session
                query = """
                    INSERT INTO chat_sessions 
                    (location, latitude, longitude, feasibility_score, recommended_technology)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (
                    session_data.get('location', 'Unknown'),
                    session_data.get('latitude'),
                    session_data.get('longitude'),
                    session_data.get('feasibility'),
                    session_data.get('recommended_technology')
                )
                cursor.execute(query, values)
                session_id = cursor.lastrowid
            
            connection.commit()
            return session_id
            
        except Error as e:
            print(f"Error saving chat session: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def save_chat_message(self, session_id, role, content, is_report=False):
        """Save a chat message"""
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO chat_messages (session_id, role, content, is_report)
                VALUES (%s, %s, %s, %s)
            """
            # Truncate very long content to avoid database errors
            truncated_content = content[:4000] if content else ""
            values = (session_id, role, truncated_content, is_report)
            cursor.execute(query, values)
            connection.commit()
            return True
            
        except Error as e:
            print(f"Error saving chat message: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_chat_sessions(self, limit=20, offset=0):
        """Get list of chat sessions"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM chat_sessions 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            sessions = cursor.fetchall()
            
            # Convert datetime objects to strings for JSON serialization
            for session in sessions:
                if session.get('created_at'):
                    session['created_at'] = session['created_at'].isoformat()
                if session.get('updated_at'):
                    session['updated_at'] = session['updated_at'].isoformat()
                    
            return sessions
            
        except Error as e:
            print(f"Error getting chat sessions: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_chat_messages(self, session_id):
        """Get messages for a specific session"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY timestamp ASC
            """
            cursor.execute(query, (session_id,))
            messages = cursor.fetchall()
            
            # Convert datetime objects to strings for JSON serialization
            for message in messages:
                if message.get('timestamp'):
                    message['timestamp'] = message['timestamp'].isoformat()
                    
            return messages
            
        except Error as e:
            print(f"Error getting chat messages: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_recent_chat_history(self, session_id, max_messages=8):
        """Get recent messages for context"""
        connection = self.get_connection()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT role, content 
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            cursor.execute(query, (session_id, max_messages))
            messages = cursor.fetchall()
            # Reverse to get chronological order
            return list(reversed(messages))
            
        except Error as e:
            print(f"Error getting recent chat history: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_session_by_id(self, session_id):
        """Get a specific session by ID"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM chat_sessions WHERE id = %s"
            cursor.execute(query, (session_id,))
            session = cursor.fetchone()
            
            if session and session.get('created_at'):
                session['created_at'] = session['created_at'].isoformat()
            if session and session.get('updated_at'):
                session['updated_at'] = session['updated_at'].isoformat()
                
            return session
            
        except Error as e:
            print(f"Error getting session by ID: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def delete_session(self, session_id):
        """Delete a session and all its messages"""
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            
            # First delete messages (due to foreign key constraint)
            delete_messages_query = "DELETE FROM chat_messages WHERE session_id = %s"
            cursor.execute(delete_messages_query, (session_id,))
            
            # Then delete the session
            delete_session_query = "DELETE FROM chat_sessions WHERE id = %s"
            cursor.execute(delete_session_query, (session_id,))
            
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error deleting session: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()