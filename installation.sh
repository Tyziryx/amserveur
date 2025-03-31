#!/bin/bash
# installation.sh - Install required dependencies for Admin Monitoring System

# Update package lists
sudo apt-get update

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
pip3 install python-daemon

# Make directories if they don't exist
mkdir -p website/static website/templates sondes parseur stockage graphiques

echo "Installation complete!"
echo "You can now start the application by running: python3 ams.py"