#!/usr/bin/env python3
"""
WSL Environment Setup Script for Scribe.

This script checks and configures the WSL environment for:
1. Audio support (PulseAudio)
2. X11 forwarding
3. Required packages
"""

import os
import sys
import subprocess
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_wsl() -> bool:
    """Check if running in WSL environment."""
    return 'WSL_DISTRO_NAME' in os.environ

def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command safely."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"Error output: {e.stderr}")
        if check:
            raise
        return e
    except Exception as e:
        logger.error(f"Error running command {cmd}: {e}")
        if check:
            raise
        return None

def check_packages() -> Dict[str, bool]:
    """Check required packages."""
    packages = {
        'pulseaudio': False,
        'alsa-utils': False,
        'xdotool': False,
        'x11-xserver-utils': False
    }
    
    for pkg in packages:
        try:
            result = run_command(['dpkg', '-s', pkg], check=False)
            packages[pkg] = result and result.returncode == 0
        except:
            pass
            
    return packages

def install_packages(missing_packages: List[str]):
    """Install required packages."""
    if not missing_packages:
        return
        
    logger.info("Installing required packages...")
    try:
        run_command(['sudo', 'apt-get', 'update'])
        run_command(['sudo', 'apt-get', 'install', '-y'] + missing_packages)
    except Exception as e:
        logger.error(f"Failed to install packages: {e}")
        raise

def setup_pulseaudio():
    """Configure PulseAudio for WSL."""
    logger.info("Setting up PulseAudio...")
    
    # Create config directory
    os.makedirs(os.path.expanduser('~/.config/pulse'), exist_ok=True)
    
    # Create client config
    config_path = os.path.expanduser('~/.config/pulse/client.conf')
    config_content = """
# PulseAudio client config for WSL
default-server = unix:/tmp/pulse-socket
autospawn = no
daemon-binary = /bin/true
enable-shm = false
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    # Start PulseAudio if not running
    try:
        run_command(['pulseaudio', '--check'], check=False)
    except:
        try:
            run_command(['pulseaudio', '--start', '--exit-idle-time=-1'])
            logger.info("Started PulseAudio server")
        except Exception as e:
            logger.error(f"Failed to start PulseAudio: {e}")

def setup_x11():
    """Configure X11 forwarding."""
    logger.info("Setting up X11 forwarding...")
    
    # Check DISPLAY variable
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':0'
        
    # Test X11 connection
    try:
        run_command(['xdpyinfo'], check=True)
        logger.info("X11 forwarding is working")
    except:
        logger.error("X11 forwarding not working. Please ensure:")
        logger.error("1. VcXsrv or similar X server is running on Windows")
        logger.error("2. DISPLAY environment variable is set correctly")
        return False
        
    return True

def main():
    """Main setup function."""
    if not check_wsl():
        logger.error("This script must be run in WSL")
        sys.exit(1)
    
    logger.info("Checking WSL environment setup...")
    
    # Check and install required packages
    packages = check_packages()
    missing = [pkg for pkg, installed in packages.items() if not installed]
    
    if missing:
        logger.info(f"Missing packages: {missing}")
        try:
            install_packages(missing)
        except Exception as e:
            logger.error(f"Package installation failed: {e}")
            sys.exit(1)
    
    # Setup audio
    try:
        setup_pulseaudio()
    except Exception as e:
        logger.error(f"Audio setup failed: {e}")
        sys.exit(1)
    
    # Setup X11
    try:
        if not setup_x11():
            sys.exit(1)
    except Exception as e:
        logger.error(f"X11 setup failed: {e}")
        sys.exit(1)
    
    logger.info("WSL environment setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())