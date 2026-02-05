# Raspberry Pi Deployment Guide

This guide walks through deploying the habit tracker to a Raspberry Pi Zero with Waveshare 1.44" LCD HAT.

## Prerequisites

- Raspberry Pi Zero (W or WH for WiFi)
- Waveshare 1.44" LCD HAT (ST7735S, 128x128)
- MicroSD card (8GB+ recommended)
- Power supply (micro USB, 5V 2A+)
- Laptop with SD card reader

---

## Step 1: Flash Raspberry Pi OS

### 1.1 Download Raspberry Pi Imager

- Get it from: https://www.raspberrypi.com/software/
- Install on your laptop

### 1.2 Flash OS to SD Card

1. Insert microSD card into laptop
2. Open Raspberry Pi Imager
3. Choose OS: **Raspberry Pi OS Lite (64-bit)** - headless, no desktop
4. Choose Storage: Your microSD card
5. Click gear icon (⚙️) for Advanced Options:
   - Set hostname: `habit-tracker`
   - **Enable SSH** ✅
   - Set username: `pi`
   - Set password: (choose a password)
   - Configure WiFi:
     - SSID: Your WiFi network name
     - Password: Your WiFi password
   - Set locale: Your timezone
6. Click **Write** and wait (~5-10 minutes)

### 1.3 Boot the Pi

1. Remove SD card from laptop
2. Insert into Raspberry Pi Zero
3. Connect LCD HAT to GPIO pins
4. Power on the Pi (wait 1-2 minutes for first boot)

---

## Step 2: SSH into Pi

### 2.1 Find Pi's IP Address

Try one of these methods:

**Option A: Using hostname**
```bash
ping habit-tracker.local
```

**Option B: Check your router**
- Look for device named "habit-tracker" or "raspberrypi"

**Option C: Scan network**
```bash
nmap -sn 192.168.1.0/24  # Adjust to your network range
```

### 2.2 Connect via SSH

```bash
ssh pi@habit-tracker.local
# Or: ssh pi@<IP_ADDRESS>
```

Enter the password you set during imaging.

---

## Step 3: Run Setup Script

### 3.1 Copy Database (Optional)

If you want to use your existing habits/data from laptop:

```bash
# On laptop:
scp habit-tracker/habit_tracker.db pi@habit-tracker.local:/tmp/
```

### 3.2 Run Setup

```bash
# On Pi (via SSH):
curl -O https://raw.githubusercontent.com/jakeagenticbrain/habit-tracker/main/scripts/setup_pi.sh
chmod +x setup_pi.sh
./setup_pi.sh
```

This script will:
- Update system packages
- Enable SPI interface
- Configure GPIO pull-up resistors
- Clone the habit-tracker repository
- Install Python dependencies
- Create systemd service for auto-start
- Copy database if provided

**Wait for completion (~10-15 minutes)**

### 3.3 Reboot

```bash
sudo reboot
```

After reboot, the habit tracker will start automatically!

---

## Step 4: Verify It Works

### 4.1 Check Service Status

```bash
ssh pi@habit-tracker.local
sudo systemctl status habit-tracker
```

Expected output:
```
● habit-tracker.service - Habit Tracker
   Loaded: loaded (/etc/systemd/system/habit-tracker.service; enabled)
   Active: active (running) since ...
```

### 4.2 View Logs

```bash
sudo journalctl -u habit-tracker -f
```

You should see:
```
Running on Raspberry Pi - using LCD display and GPIO input
Starting app...
```

### 4.3 Test the Display

The LCD should show the home screen with the character!

### 4.4 Test the Controls

- Joystick LEFT/RIGHT: Navigate screens
- Joystick UP/DOWN: Navigate within screen
- KEY1 (Button A): Select/Confirm
- KEY2 (Button B): Back/Cancel
- KEY3 (Button C): Quick action

---

## Updating the App

### From the Pi

```bash
ssh pi@habit-tracker.local
cd habit-tracker
./scripts/update.sh
```

This pulls the latest code from GitHub and restarts the service.

### From Your Laptop

1. Make changes to code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "feat: your changes"
   git push origin main
   ```
3. SSH to Pi and run update script:
   ```bash
   ssh pi@habit-tracker.local
   cd habit-tracker
   ./scripts/update.sh
   ```

---

## Troubleshooting

### Display Not Working

1. Check SPI is enabled:
   ```bash
   ls /dev/spidev*
   ```
   Should show `/dev/spidev0.0` and `/dev/spidev0.1`

2. Enable SPI manually:
   ```bash
   sudo raspi-config
   # Interface Options → SPI → Enable
   sudo reboot
   ```

3. Check service logs:
   ```bash
   sudo journalctl -u habit-tracker -n 50
   ```

### Buttons Not Responding

1. Check GPIO pull-ups in `/boot/config.txt`:
   ```bash
   cat /boot/config.txt | grep gpio
   ```
   Should contain: `gpio=6,19,5,26,13,21,20,16=pu`

2. Add manually if missing:
   ```bash
   echo "gpio=6,19,5,26,13,21,20,16=pu" | sudo tee -a /boot/config.txt
   sudo reboot
   ```

### App Crashes on Startup

1. Check Python errors:
   ```bash
   sudo journalctl -u habit-tracker -n 100
   ```

2. Test manually:
   ```bash
   cd /home/pi/habit-tracker
   source venv/bin/activate
   PYTHONPATH=. python main.py
   ```

3. Check dependencies:
   ```bash
   pip list
   ```
   Verify `RPi.GPIO`, `spidev`, `st7735`, `Pillow` are installed

### WiFi Not Connecting

1. Check WiFi config:
   ```bash
   sudo raspi-config
   # System Options → Wireless LAN
   ```

2. Restart WiFi:
   ```bash
   sudo systemctl restart dhcpcd
   ```

---

## Advanced Configuration

### Change Auto-Start Behavior

Edit the systemd service:
```bash
sudo nano /etc/systemd/system/habit-tracker.service
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart habit-tracker
```

### Disable Auto-Start

```bash
sudo systemctl disable habit-tracker
sudo systemctl stop habit-tracker
```

### Manual Control

```bash
# Start
sudo systemctl start habit-tracker

# Stop
sudo systemctl stop habit-tracker

# Restart
sudo systemctl restart habit-tracker

# Status
sudo systemctl status habit-tracker
```

---

## GPIO Pin Reference

| Function | GPIO (BCM) | Physical Pin |
|----------|------------|--------------|
| Joystick UP | 6 | Pin 31 |
| Joystick DOWN | 19 | Pin 35 |
| Joystick LEFT | 5 | Pin 29 |
| Joystick RIGHT | 26 | Pin 37 |
| Joystick PRESS | 13 | Pin 33 |
| Button A (KEY1) | 21 | Pin 40 |
| Button B (KEY2) | 20 | Pin 38 |
| Button C (KEY3) | 16 | Pin 36 |
| Display DC | 25 | Pin 22 |
| Display RST | 27 | Pin 13 |
| Display BL | 24 | Pin 18 |

---

## Resources

- Waveshare HAT Wiki: https://www.waveshare.com/wiki/1.44inch_LCD_HAT
- Raspberry Pi Documentation: https://www.raspberrypi.com/documentation/
- Project Repository: https://github.com/jakeagenticbrain/habit-tracker
