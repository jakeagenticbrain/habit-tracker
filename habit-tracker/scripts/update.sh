#!/bin/bash
# habit-tracker/scripts/update.sh
# Pull latest code from GitHub and restart service

set -e

echo "🔄 Updating habit tracker..."

cd /home/pi/habit-tracker

# Pull latest code
git pull origin main

# Restart service
sudo systemctl restart habit-tracker

echo "✅ Update complete! App restarted."
