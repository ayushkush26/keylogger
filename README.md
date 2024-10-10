# Keylogger

## Overview
This keylogger is a Python application that captures keystrokes, mouse movements, clicks, and system information. It periodically sends reports via email and saves logs to a local file. It also includes features to capture screenshots and record audio from the microphone.

**Disclaimer**: This tool is intended for educational purposes only. Ensure you have proper permissions and legal authority to use such software. Unauthorized use of a keylogger is illegal and unethical.

## Features
- **Keystroke Logging**: Captures all keystrokes typed on the keyboard.
- **Mouse Logging**: Records mouse movements, clicks, and scrolls.
- **System Information**: Collects and logs system information (hostname, IP address, etc.).
- **Email Reporting**: Sends logs via email at specified intervals.
- **Screenshot Capture**: Takes screenshots of the current screen and saves them as image files.
- **Audio Recording**: Records audio from the microphone and saves it as a `.wav` file.

## Requirements
- Python 3.x
- Required libraries:
  - `pyscreenshot`
  - `sounddevice`
  - `pynput`
  - `smtplib`
  - `wave`
  - `logging`
  
You can install the required libraries using pip3:

```bash
pip3 install pyscreenshot sounddevice pynput
```

## Setup

1: ```bash
git clone https://github.com/yourusername/keylogger.git
cd keylogger
```

2: ```bash
export EMAIL_ADDRESS="your_email@gmail.com"
export EMAIL_PASSWORD="your_password"
```
3: ```bash
python keylogger.py
```
