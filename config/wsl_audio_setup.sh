#!/bin/bash

# WSL Audio Setup Script for Scribe
# This script configures PulseAudio for WSL2 audio support

echo "Setting up WSL2 audio..."

# Install required packages
sudo apt-get update
sudo apt-get install -y pulseaudio alsa-utils

# Create PulseAudio config for WSL
mkdir -p ~/.config/pulse
cat > ~/.config/pulse/client.conf << EOF
default-server = unix:/tmp/pulse-socket
# Prevent a server running in the container
autospawn = no
daemon-binary = /bin/true
# Prevent the use of shared memory
enable-shm = false
EOF

# Start PulseAudio server if not running
pulseaudio --check || pulseaudio --start --exit-idle-time=-1

# Test audio
echo "Testing audio setup..."
arecord -l

echo "Audio setup complete!"