# Simplified memory management for single conversation per container

import os
import json
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from langgraph.checkpoint import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

class MemoryManager:
    """Manages conversation memory with SQLite database for single conversation."""
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{db_path}")
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memory table for storing conversation data in chronological order
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_name TEXT,
                tool_args TEXT,
                tool_result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for chronological ordering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON conversation_memory(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_checkpointer(self):
        """Get the SQLite checkpointer for LangGraph."""
        return self.checkpointer
    
    def store_message(self, message: BaseMessage):
        """Store a message in the database in chronological order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        message_type = message.__class__.__name__
        content = message.content if hasattr(message, 'content') else str(message)
        
        # Extract tool information if it's a tool message
        tool_name = None
        tool_args = None
        tool_result = None
        
        if isinstance(message, ToolMessage):
            tool_name = getattr(message, 'tool_name', None)
            tool_args = json.dumps(getattr(message, 'tool_args', {}))
            tool_result = content
        
        cursor.execute('''
            INSERT INTO conversation_memory 
            (message_type, content, tool_name, tool_args, tool_result)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_type, content, tool_name, tool_args, tool_result))
        
        conn.commit()
        conn.close()
    
    def get_full_memory(self) -> List[Dict[str, Any]]:
        """Get the complete conversation memory in chronological order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, content, tool_name, tool_args, tool_result, timestamp
            FROM conversation_memory 
            ORDER BY timestamp ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        memory = []
        for row in rows:
            message_type, content, tool_name, tool_args, tool_result, timestamp = row
            
            memory_item = {
                "type": message_type,
                "content": content,
                "timestamp": timestamp
            }
            
            if tool_name:
                memory_item["tool_name"] = tool_name
                memory_item["tool_args"] = json.loads(tool_args) if tool_args else {}
                memory_item["tool_result"] = tool_result
            
            memory.append(memory_item)
        
        return memory
    
    def clear_memory(self):
        """Clear all memory from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM conversation_memory')
        
        conn.commit()
        conn.close()

# Global memory manager instance
memory_manager = MemoryManager()

def get_memory_manager():
    """Get the global memory manager instance."""
    return memory_manager

def get_checkpointer():
    """Get the SQLite checkpointer for LangGraph."""
    return memory_manager.get_checkpointer()

# Convenience functions for API endpoints
def get_full_memory():
    """Get full memory for API endpoint."""
    return memory_manager.get_full_memory()

def clear_memory():
    """Clear memory for API endpoint."""
    return memory_manager.clear_memory() 