"""
Single Instance Manager - Ensures only one Scribe instance runs at a time.

Uses a lock file with PID and version info. If a newer version starts,
it can terminate older instances gracefully.
"""

import os
import sys
import psutil
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SingleInstanceManager:
    """
    Manages single instance enforcement with version-aware upgrades.
    
    Features:
    - Lock file with PID and version
    - Detects stale locks (process not running)
    - Allows newer versions to replace older ones
    - Graceful termination of old instances
    """
    
    def __init__(self, app_name: str = "scribe", version: str = "unknown"):
        """
        Initialize single instance manager.
        
        Args:
            app_name: Name of the application
            version: Current version string
        """
        self.app_name = app_name
        self.version = version
        self.lock_file = self._get_lock_path()
        self.acquired = False
    
    def _get_lock_path(self) -> Path:
        """Get path to lock file in temp or data directory."""
        if sys.platform == "win32":
            # Windows: Use TEMP or data directory
            temp_dir = Path(os.environ.get('TEMP', os.environ.get('TMP', 'data')))
        else:
            # Unix: Use /tmp or /var/run
            temp_dir = Path('/tmp')
        
        return temp_dir / f".{self.app_name}.lock"
    
    def _read_lock_info(self) -> Optional[Tuple[int, str]]:
        """
        Read PID and version from lock file.
        
        Returns:
            (pid, version) tuple or None if lock doesn't exist/invalid
        """
        try:
            if not self.lock_file.exists():
                return None
            
            content = self.lock_file.read_text().strip()
            if not content:
                return None
            
            parts = content.split('|')
            if len(parts) != 2:
                return None
            
            pid = int(parts[0])
            version = parts[1]
            return (pid, version)
        except Exception as e:
            logger.warning(f"Failed to read lock file: {e}")
            return None
    
    def _write_lock_info(self):
        """Write current PID and version to lock file."""
        try:
            pid = os.getpid()
            content = f"{pid}|{self.version}"
            self.lock_file.write_text(content)
            self.acquired = True
            logger.info(f"Acquired instance lock: PID={pid}, version={self.version}")
        except Exception as e:
            logger.error(f"Failed to write lock file: {e}")
            raise
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            process = psutil.Process(pid)
            
            # Check if it's actually a Python process running Scribe
            try:
                cmdline = ' '.join(process.cmdline()).lower()
                # Check for Python process with scribe-related commands
                is_python = 'python' in cmdline
                is_scribe = 'scribe' in cmdline or 'run_scribe' in cmdline
                
                if is_python and is_scribe:
                    return True
                
                # Also check exe name in case cmdline is empty
                exe_name = process.name().lower()
                if 'python' in exe_name:
                    # If it's a Python process but cmdline is empty/unclear,
                    # check if it has the same working directory
                    try:
                        cwd = process.cwd().lower()
                        if 'scribe' in cwd:
                            return True
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
            return False
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _terminate_process(self, pid: int) -> bool:
        """
        Attempt to gracefully terminate a process.
        
        Args:
            pid: Process ID to terminate
            
        Returns:
            True if terminated successfully
        """
        try:
            process = psutil.Process(pid)
            logger.info(f"Terminating old Scribe instance (PID={pid})...")
            
            # Try graceful termination first
            process.terminate()
            
            # Wait up to 3 seconds for graceful shutdown
            try:
                process.wait(timeout=3)
                logger.info("Old instance terminated gracefully")
                return True
            except psutil.TimeoutExpired:
                # Force kill if still running
                logger.warning("Graceful termination timed out, forcing kill...")
                process.kill()
                process.wait(timeout=2)
                logger.info("Old instance force-killed")
                return True
                
        except psutil.NoSuchProcess:
            logger.info("Old instance already gone")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate old instance: {e}")
            return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.
        
        Returns:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        try:
            # Simple version comparison (assumes semantic versioning)
            def version_tuple(v):
                # Strip alpha/beta suffixes for comparison
                clean_v = v.split('-')[0]
                return tuple(map(int, clean_v.split('.')))
            
            v1_tuple = version_tuple(v1)
            v2_tuple = version_tuple(v2)
            
            if v1_tuple < v2_tuple:
                return -1
            elif v1_tuple > v2_tuple:
                return 1
            else:
                return 0
        except Exception:
            # If version parsing fails, treat as equal
            return 0
    
    def acquire(self) -> bool:
        """
        Acquire single instance lock.
        
        Returns:
            True if lock acquired (either new or upgraded from old version)
            False if another instance is running and cannot be replaced
        """
        lock_info = self._read_lock_info()
        
        if lock_info is None:
            # No existing lock or invalid - acquire it
            logger.info("No existing instance found, acquiring lock")
            self._write_lock_info()
            return True
        
        old_pid, old_version = lock_info
        
        # Check if old process is still running
        if not self._is_process_running(old_pid):
            logger.info(f"Stale lock found (PID={old_pid}), replacing it")
            self._write_lock_info()
            return True
        
        # Old process is running - compare versions
        version_cmp = self._compare_versions(self.version, old_version)
        
        if version_cmp > 0:
            # We're newer - terminate old instance
            logger.info(f"Newer version detected (old={old_version}, new={self.version})")
            if self._terminate_process(old_pid):
                self._write_lock_info()
                return True
            else:
                logger.error("Failed to terminate old instance")
                return False
        
        elif version_cmp == 0:
            # Same version already running
            logger.warning(f"Scribe v{old_version} is already running (PID={old_pid})")
            return False
        
        else:
            # Older version trying to start - don't allow
            logger.warning(f"Newer version already running (current={old_version}, attempted={self.version})")
            return False
    
    def release(self):
        """Release the instance lock."""
        if self.acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink()
                self.acquired = False
                logger.info("Released instance lock")
            except Exception as e:
                logger.error(f"Failed to release lock: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            raise RuntimeError("Another instance of Scribe is already running")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
