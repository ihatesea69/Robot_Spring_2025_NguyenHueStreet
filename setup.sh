#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3-pip \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libilmbase23 \
    libopenexr23 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5

# Install Python dependencies
pip3 install -r requirements.txt

# Set up permissions for serial port (for LD2410 sensor)
sudo usermod -a -G dialout $USER 