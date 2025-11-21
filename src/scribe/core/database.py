"""
Database Management for Scribe's Conversation Memory.

Handles SQLite connection, schema creation, and data access.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages the SQLite database for conversation history."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the DatabaseManager.

        Args:
            db_path: Path to the SQLite database file. Defaults to ~/.scribe/data/scribe.db
        """
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = Path.home() / ".scribe" / "data" / "scribe.db"
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Successfully connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}", exc_info=True)
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

    def create_schema(self):
        """Create the necessary tables and indexes for the conversation memory."""
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            
            # Create transcriptions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                text TEXT NOT NULL,
                application TEXT,
                window_title TEXT,
                audio_duration REAL,
                word_count INTEGER,
                character_count INTEGER,
                confidence REAL,
                language TEXT,
                used_plugin TEXT,
                ai_formatted BOOLEAN,
                raw_text TEXT,
                quality_rating INTEGER,
                quality_feedback TEXT,
                audio_file TEXT
            );
            """)

            # Create FTS5 table for full-text search
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS transcriptions_fts USING fts5(
                text,
                application,
                window_title,
                content='transcriptions',
                content_rowid='id'
            );
            """)

            # Create triggers to keep FTS table in sync
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcriptions_after_insert
            AFTER INSERT ON transcriptions
            BEGIN
                INSERT INTO transcriptions_fts(rowid, text, application, window_title)
                VALUES (new.id, new.text, new.application, new.window_title);
            END;
            """)

            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcriptions_after_delete
            AFTER DELETE ON transcriptions
            BEGIN
                INSERT INTO transcriptions_fts(transcriptions_fts, rowid, text, application, window_title)
                VALUES ('delete', old.id, old.text, old.application, old.window_title);
            END;
            """)

            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transcriptions_after_update
            AFTER UPDATE ON transcriptions
            BEGIN
                INSERT INTO transcriptions_fts(transcriptions_fts, rowid, text, application, window_title)
                VALUES ('delete', old.id, old.text, old.application, old.window_title);
                INSERT INTO transcriptions_fts(rowid, text, application, window_title)
                VALUES (new.id, new.text, new.application, new.window_title);
            END;
            """)
            
            self.conn.commit()
            logger.info("Database schema created/verified successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating database schema: {e}", exc_info=True)
            self.conn.rollback()
            raise

    def search_transcriptions(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Perform a full-text search on the transcriptions.

        Args:
            search_term: The term to search for.

        Returns:
            A list of matching transcription records.
        """
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM transcriptions_fts WHERE transcriptions_fts MATCH ? ORDER BY rank",
                (search_term,)
            )
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            logger.error(f"Error searching transcriptions: {e}", exc_info=True)
            return []