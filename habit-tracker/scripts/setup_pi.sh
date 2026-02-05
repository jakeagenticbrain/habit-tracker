#!/bin/bash
# habit-tracker/scripts/setup_pi.sh
# Initial setup for Raspberry Pi deployment

set -e

echo "🚀 Setting up Habit Tracker on Raspberry Pi..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip if not present
echo "🐍 Installing Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Enable SPI interface
echo "⚙️ Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Add GPIO pull-up resistors to /boot/config.txt
if ! grep -q "gpio=6,19,5,26,13,21,20,16=pu" /boot/config.txt; then
    echo "🔧 Configuring GPIO pull-ups..."
    echo "gpio=6,19,5,26,13,21,20,16=pu" | sudo tee -a /boot/config.txt
fi

# Clone repository
if [ ! -d "/home/pi/habit-tracker" ]; then
    echo "📥 Cloning repository..."
    cd /home/pi
    git clone https://github.com/jakeagenticbrain/habit-tracker.git
    cd habit-tracker
else
    echo "📂 Repository already exists, pulling latest..."
    cd /home/pi/habit-tracker
    git pull origin main
fi

# Create virtual environment
echo "🔨 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements-pi.txt

# Copy database from laptop if provided
if [ -f "/tmp/habit_tracker.db" ]; then
    echo "💾 Copying database from laptop..."
    cp /tmp/habit_tracker.db /home/pi/habit-tracker/habit_tracker.db
fi

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/habit-tracker.service > /dev/null <<EOF
[Unit]
Description=Habit Tracker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/habit-tracker
Environment="PYTHONPATH=/home/pi/habit-tracker"
ExecStart=/home/pi/habit-tracker/venv/bin/python /home/pi/habit-tracker/main.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Enabling auto-start..."
sudo systemctl daemon-reload
sudo systemctl enable habit-tracker
sudo systemctl start habit-tracker

echo ""
echo "✅ Setup complete!"
echo ""
echo "Commands:"
echo "  sudo systemctl status habit-tracker   # Check status"
echo "  sudo systemctl restart habit-tracker  # Restart app"
echo "  sudo systemctl stop habit-tracker     # Stop app"
echo "  ./scripts/update.sh                   # Pull latest code and restart"
echo ""
echo "⚠️ IMPORTANT: Reboot required for GPIO pull-ups to take effect"
echo "   Run: sudo reboot"
