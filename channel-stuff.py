import random
import time
import threading
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from cryptography.fernet import Fernet

# Encryption key
key = b'54oT35JMsig5f6iha0Sv-dp78zr5A-xom11A5M39RO0='
cipher_suite = Fernet(key)

# Define the master key and URLs
encrypted_master_key = 'gAAAAABnt6OH8Jz8Xc-DKO9z9BAe4wC3fhaev8LHwvqNNHxw-RfX5iZfbB9kYFfiIRGV5igVj4PNRPz3cyHs-XDAxk_vXxybwJDgjYOXc63mDv_zKMrOBF0IK5s6xMSHbwt2KZ7a6gV7iQKDFdHSj8U4ssfapaGhLw=='
MASTER_KEY = cipher_suite.decrypt(encrypted_master_key.encode()).decode()
CHANNELS_URL = 'https://api.jsonbin.io/v3/b/67cd3df4ad19ca34f8190431'
USER_CREDENTIALS_URL = 'https://api.jsonbin.io/v3/b/67b8748dacd3cb34a8eb2435'


class Radio:
    def __init__(self, json_bin_url, api_key):
        self.json_bin_url = json_bin_url
        self.api_key = api_key
        self.channels = {
            9: "476.625 MHz",
            12: "476.700 MHz",
            13: "476.725 MHz",
            14: "476.750 MHz",
            15: "476.775 MHz",
            16: "476.800 MHz",
            17: "476.825 MHz",
            19: "476.875 MHz",
            20: "476.900 MHz",
            21: "476.925 MHz",
            24: "477.000 MHz",
            25: "477.025 MHz",
            26: "477.050 MHz",
            27: "477.075 MHz",
            28: "477.100 MHz",
            30: "477.150 MHz",
            39: "477.375 MHz",
            49: "476.6375 MHz",
            50: "476.6625 MHz",
            51: "476.6875 MHz",
            52: "476.7125 MHz",
            53: "476.7375 MHz",
            54: "476.7625 MHz",
            55: "476.7875 MHz",
            56: "476.8125 MHz",
            57: "476.8375 MHz",
            58: "476.8625 MHz",
            59: "476.8875 MHz",
            60: "476.9125 MHz",
            64: "477.0125 MHz",
            65: "477.0375 MHz",
            66: "477.0625 MHz",
            67: "477.0875 MHz",
            68: "477.1125 MHz",
            69: "477.1375 MHz",
            70: "477.1625 MHz",
            79: "477.3875 MHz",
            80: "477.4125 MHz",
        }
        self.current_channel = 9
        self.app = None
        self.team = None

    def set_app(self, app):
        self.app = app

    def set_team(self, team):
        self.team = team

    def login(self, username, password):
        headers = {
            'X-Master-Key': MASTER_KEY
        }
        try:
            response = requests.get(USER_CREDENTIALS_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
            users = data.get('record', {}).get('users', [])
            for user in users:
                if user['username'] == username and user['password'] == password:
                    return True
            return False
        except requests.RequestException as e:
            print(f"Error fetching user credentials: {e}")
            return False

    def display_channels(self):
        channels_info = "Available Channels:\n"
        for channel, frequency in self.channels.items():
            channels_info += f"Channel {channel}: {frequency}\n"
        return channels_info

    def get_current_channel(self):
        if not self.team:
            print("No team selected.")
            return
        response = requests.get(self.json_bin_url, headers={"X-Master-Key": self.api_key})
        if response.status_code == 200:
            data = response.json()
            self.current_channel = data.get('record', {}).get('teams', {}).get(self.team, {}).get("current_channel", self.current_channel)
            print(f"Retrieved current channel for {self.team}: {self.current_channel}")
        else:
            print("Failed to retrieve current channel information.")

    def update_current_channel(self):
        if not self.team:
            print("No team selected.")
            return
        response = requests.get(self.json_bin_url, headers={"X-Master-Key": self.api_key})
        if response.status_code == 200:
            data = response.json()
            teams = data.get('record', {}).get('teams', {})
            used_channels = {team_info['current_channel'] for team_info in teams.values()}
            available_channels = [ch for ch in self.channels.keys() if ch not in used_channels]
            if not available_channels:
                print("No available channels.")
                return
            new_channel = random.choice(available_channels)
            self.current_channel = new_channel
            teams[self.team] = {"current_channel": self.current_channel}
            data = {"teams": teams}
            response = requests.put(self.json_bin_url, json=data, headers={"X-Master-Key": self.api_key})
            if response.status_code == 200:
                print(f"Changed to Channel {new_channel} for {self.team}: {self.channels[new_channel]}")
            else:
                print("Failed to update current channel information.")
        else:
            print("Failed to retrieve current channel information.")

    def current_channel_info(self):
        self.get_current_channel()
        channel_info = self.channels[self.current_channel]
        return f"Currently tuned to Channel {self.current_channel}: {channel_info}"

    def periodic_channel_change(self, interval):
        while True:
            time.sleep(interval)
            self.update_current_channel()
            self.alert_users()

    def alert_users(self):
        print(f"Alert: Channel changed to {self.current_channel} for {self.team}: {self.channels[self.current_channel]}")
        if self.app:
            self.app.update_current_channel_info()

class RadioApp:
    def __init__(self, root, radio):
        self.root = root
        self.radio = radio
        self.radio.set_app(self)
        self.root.title("Radio Dashboard")

        self.login_frame = ttk.Frame(root, padding=20)
        self.team_selection_frame = ttk.Frame(root, padding=20)
        self.dashboard_frame = ttk.Frame(root, padding=20)

        self.create_login_frame()
        self.create_team_selection_frame()
        self.create_dashboard_frame()

        self.login_frame.pack()

    def create_login_frame(self):
        ttk.Label(self.login_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, font=("Helvetica", 12))
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.login_frame, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", font=("Helvetica", 12))
        self.password_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login, bootstyle=SUCCESS).grid(row=2, columnspan=2, pady=10)

    def create_team_selection_frame(self):
        ttk.Label(self.team_selection_frame, text="Select Team:", font=("Helvetica", 12)).pack(pady=10)

        ttk.Button(self.team_selection_frame, text="Team A", command=lambda: self.select_team("Team A"), bootstyle=INFO).pack(pady=5)
        ttk.Button(self.team_selection_frame, text="Team B", command=lambda: self.select_team("Team B"), bootstyle=INFO).pack(pady=5)
        ttk.Button(self.team_selection_frame, text="Team C", command=lambda: self.select_team("Team C"), bootstyle=INFO).pack(pady=5)

    def create_dashboard_frame(self):
        self.current_channel_label = ttk.Label(self.dashboard_frame, text="Currently tuned to", font=("Helvetica", 10))
        self.current_channel_label.pack(pady=5)

        self.channel_label = ttk.Label(self.dashboard_frame, text="", font=("Helvetica", 16, "bold"))
        self.channel_label.pack(pady=5)

        self.frequency_label = ttk.Label(self.dashboard_frame, text="", font=("Helvetica", 24, "bold"))
        self.frequency_label.pack(pady=10)

        ttk.Button(self.dashboard_frame, text="Update", command=self.update_frequency, bootstyle=INFO).pack(side=LEFT, padx=5, pady=5)
        ttk.Button(self.dashboard_frame, text="Info", command=self.display_channels, bootstyle=INFO).pack(side=RIGHT, padx=5, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.radio.login(username, password):
            self.login_frame.pack_forget()
            self.team_selection_frame.pack()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def select_team(self, team):
        self.radio.set_team(team)
        self.team_selection_frame.pack_forget()
        self.dashboard_frame.pack()
        self.update_current_channel_info()
        threading.Thread(target=self.radio.periodic_channel_change, args=(30,), daemon=True).start()

    def update_current_channel_info(self):
        self.radio.get_current_channel()
        self.current_channel_label.config(text="Currently tuned to")
        self.channel_label.config(text=f"Channel {self.radio.current_channel}")
        self.frequency_label.config(text=self.radio.channels[self.radio.current_channel])
        print(f"Updated GUI to Channel {self.radio.current_channel}: {self.radio.channels[self.radio.current_channel]}")

    def update_frequency(self):
        self.radio.update_current_channel()
        self.update_current_channel_info()

    def display_channels(self):
        channels_info = self.radio.display_channels()
        messagebox.showinfo("Channels", channels_info)

def main():
    json_bin_url = CHANNELS_URL  # Replace with your JSON bin URL
    api_key = MASTER_KEY  # Replace with your JSON bin API key

    radio = Radio(json_bin_url, api_key)
    root = ttk.Window(themename="superhero")
    app = RadioApp(root, radio)
    root.mainloop()

if __name__ == "__main__":
    main()