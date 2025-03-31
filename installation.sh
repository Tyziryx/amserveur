#!/bin/bash
# install_deps.sh - Install required dependencies for Admin Monitoring System

# Update package lists
sudo apt-get update -y

# Install Python and required system packages
sudo apt-get install -y python3 python3-pip python3-dev sqlite3

# Install system packages for graphics
sudo apt-get install -y libfreetype6-dev pkg-config

# Install Python packages
pip3 install psutil
pip3 install pandas
pip3 install matplotlib
pip3 install flask
pip3 install requests
pip3 install beautifulsoup4
pip3 install lxml

# Fix ams.py Linux compatibility issue with creationflags
if grep -q "creationflags=" ams.py; then
  echo "Fixing ams.py for Linux compatibility..."
  sed -i 's/creationflags=subprocess.CREATE_NO_WINDOW//' ams.py
  sed -i 's/creationflags=flags//' ams.py
fi

# Fix app.py Linux compatibility issue with creationflags
if grep -q "creationflags=" website/app.py; then
  echo "Fixing website/app.py for Linux compatibility..."
  sed -i 's/creationflags=subprocess.CREATE_NO_WINDOW//' website/app.py
fi

echo "Installation complete! You can now run: python3 ams.py"