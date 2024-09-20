set -e

# Fetch latest package lists
apt-get update

# Install build tools
apt-get install -y build-essential m4 git cmake locales

# Install PrusaSlicer dependencies
apt-get install -y libglu1-mesa-dev libgtk-4-dev libdbus-1-dev libwebkit2gtk-4.1-dev  texinfo autoconf automake libtool

# Install Python3 for runner.py
apt-get install -y python3 python3-yaml