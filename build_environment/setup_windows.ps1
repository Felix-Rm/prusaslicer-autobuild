# Install chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Visual Studio 2019 Build Tools
choco install -y visualstudio2019buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.ATLMFC --includeRecommended --includeOptional --quiet --wait --norestart" 

# Install vswhere (for build environment discovery)
choco install -y vswhere 

# Install Git and CMake for setup and build
choco install -y git 
choco install -y cmake --installargs 'ADD_CMAKE_TO_PATH=System'

# Install Python3 and PyYAML for setup
choco install -y python3
python -m pip install pyyaml