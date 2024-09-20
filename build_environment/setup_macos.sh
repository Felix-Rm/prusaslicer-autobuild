set -e

# Install xcode
xcode-select --install || true

# Install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install build tools
brew install cmake make git

# Install PrusaSlicer dependencies
brew install m4 zlib autoconf

# MPFR needs automake 1.16.5
curl -L http://ftpmirror.gnu.org/automake/automake-1.16.5.tar.gz | tar -xz automake-1.16.5
cd automake-1.16.5 && ./configure && sudo make install

# Install Python3 for runner.py
brew install python3
python3 -m pip install pyyaml --break-system-packages