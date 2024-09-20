# Install xcode
xcode-select --install

# Install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install build tools
brew install cmake git

# Install PrusaSlicer dependencies
brew install m4 zlib automake autoconf libtool
ln -s /opt/homebrew/bin/automake /opt/homebrew/bin/automake-1.16

echo $(automake-1.16 --version)

# Install Python3 for runner.py
brew install python3 pyyaml