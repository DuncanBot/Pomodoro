import time
import json
import os
import threading
import tkinter as tk
from tkinter import messagebox
import pygame  # Import the pygame library

# Constants for the Pomodoro
WORK_DURATION = 25 * 60  # 25 minutes
SHORT_BREAK_DURATION = 5 * 60  # 5 minutes
LONG_BREAK_DURATION = 15 * 60  # 15 minutes
POMODOROS_BEFORE_LONG_BREAK = 4

# File to save completed sessions
SESSION_FILE = "pomodoro_sessions.json"

class PomodoroApp:
    def __init__(self, base):
        self.root = base
        self.root.title("Pomodoro Timer")
        self.root.geometry("300x200")

        self.completed_sessions = self.load_sessions()
        self.pomodoro_count = 0
        self.current_timer = None
        self.is_running = False
        self.time_left = WORK_DURATION

        # Initialize pygame mixer for sound
        pygame.mixer.init()

        # Create GUI elements
        self.label = tk.Label(base, text="Pomodoro Timer", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.time_label = tk.Label(base, text="25:00", font=("Helvetica", 24))
        self.time_label.pack(pady=5)

        self.start_button = tk.Button(base, text="Start", command=self.start_timer)
        self.start_button.pack(side="left", padx=20)

        self.pause_button = tk.Button(base, text="Pause", command=self.pause_timer)
        self.pause_button.pack(side="left", padx=20)

        self.resume_button = tk.Button(base, text="Resume", command=self.resume_timer)
        self.resume_button.pack(side="left", padx=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    @staticmethod
    def load_sessions():
        # Load the number of completed sessions from a file
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                return json.load(f).get("completed_sessions", 0)
        else:
            return 0

    def save_sessions(self):
        # Save the number of completed sessions to a file
        with open(SESSION_FILE, "w") as f:
            json.dump({"completed_sessions": self.completed_sessions}, f)

    def start_timer(self):
        # Start the Pomodoro timer
        if not self.is_running:
            self.is_running = True
            self.time_left = WORK_DURATION
            self.run_timer()

    def pause_timer(self):
        # Pause the timer
        if self.is_running:
            self.is_running = False
            if self.current_timer:
                self.root.after_cancel(self.current_timer)
                self.current_timer = None

    def resume_timer(self):
        # Resume the paused timer
        if not self.is_running and self.time_left > 0:
            self.is_running = True
            self.run_timer()

    def run_timer(self):
        # Timer countdown
        mins, secs = divmod(self.time_left, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")
        if self.time_left > 0:
            self.time_left -= 1
            self.current_timer = self.root.after(1000, self.run_timer)
        else:
            self.is_running = False
            self.completed_sessions += 1
            self.save_sessions()
            self.pomodoro_count += 1
            self.play_notification()
            self.switch_sessions()

    def switch_sessions(self):
        # Switch between work and break sessions
        if self.pomodoro_count % POMODOROS_BEFORE_LONG_BREAK == 0:
            self.time_left = LONG_BREAK_DURATION
            messagebox.showinfo("Pomodoro Timer", "Time for a long break! Rest for 15 minutes.")
        else:
            self.time_left = SHORT_BREAK_DURATION
            messagebox.showinfo("Pomodoro Timer", "Take a short break for 5 minutes.")
        self.run_timer()

    @staticmethod
    def play_notification():
        # Play a sound notification when a session ends
        try:
            pygame.mixer.music.load("notification_sound.mp3")  # Load the sound file
            pygame.mixer.music.play()  # Play the sound
        except Exception as e:
            print(f"Notification sound could not be played: {e}")

    def on_closing(self):
        # Handle closing the app
        if messagebox.askokcancel("Quit", "Do you want to quit the Pomodoro timer?"):
            if self.current_timer:
                self.root.after_cancel(self.current_timer)
            pygame.mixer.quit()  # Quit the pygame mixer
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
