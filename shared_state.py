"""
Shared state management for Discord bot and API server
"""
from datetime import datetime
from typing import Optional, Dict, Any
import threading

class DecoyStatusManager:
    """Thread-safe manager for decoy status state"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_decoy_status: Optional[str] = "OFF"  # Default to OFF when no events found
        self._latest_message_time: Optional[datetime] = None
        self._status_message_id: Optional[int] = None
        self._check_interval: int = 5
        self._last_check_time: Optional[datetime] = None
        self._bot_online: bool = False
        
    def update_status(self, status: str, message_time: datetime, message_id: Optional[int] = None) -> None:
        """Update the decoy status"""
        with self._lock:
            self._latest_decoy_status = status
            self._latest_message_time = message_time
            if message_id:
                self._status_message_id = message_id
            self._last_check_time = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current decoy status"""
        with self._lock:
            return {
                'status': self._latest_decoy_status,
                'last_update': self._latest_message_time.isoformat() if self._latest_message_time else None,
                'last_check': self._last_check_time.isoformat() if self._last_check_time else None,
                'bot_online': self._bot_online,
                'check_interval': self._check_interval
            }
    
    def set_bot_online(self, online: bool) -> None:
        """Set bot online status"""
        with self._lock:
            self._bot_online = online
    
    def set_check_interval(self, interval: int) -> None:
        """Set check interval"""
        with self._lock:
            self._check_interval = interval
    
    def get_check_interval(self) -> int:
        """Get check interval"""
        with self._lock:
            return self._check_interval
    
    def get_status_message_id(self) -> Optional[int]:
        """Get status message ID"""
        with self._lock:
            return self._status_message_id
    
    def set_status_message_id(self, message_id: Optional[int]) -> None:
        """Set status message ID"""
        with self._lock:
            self._status_message_id = message_id

# Global shared state instance
decoy_status_manager = DecoyStatusManager()
