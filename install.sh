#!/bin/bash

# Create installation directory
INSTALL_DIR="/opt/robot-emotion"
sudo mkdir -p $INSTALL_DIR

# Copy application files
sudo cp -r modules/ utils/ resources/ $INSTALL_DIR/
sudo cp main.py requirements.txt $INSTALL_DIR/

# Set permissions
sudo chown -R $USER:$USER $INSTALL_DIR
sudo chmod -R 755 $INSTALL_DIR

# Create symbolic link to executable
sudo ln -sf $INSTALL_DIR/main.py /usr/local/bin/robot-emotion

# Make the main script executable
sudo chmod +x $INSTALL_DIR/main.py 