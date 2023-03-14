import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import concurrent.futures
import subprocess
import re
import os

class App:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Playlist Downloader")

        self.absolute_path_file = os.path.abspath(__file__)
        self.folder_path = os.path.dirname(self.absolute_path_file)

        self.playlist_url_label = tk.Label(master, text="Playlist URL:")
        self.playlist_url_label.pack()

        self.playlist_url_entry = tk.Entry(master, width=100)
        self.playlist_url_entry.pack()

        self.start_video_number_label = tk.Label(master, text="Start Video Number:")
        self.start_video_number_label.pack()

        self.start_video_number_entry = tk.Entry(master, width=10)
        self.start_video_number_entry.insert(0,1)
        self.start_video_number_entry.pack()

        self.audio_only_var = tk.BooleanVar(value=False)
        self.audio_only_checkbox = tk.Checkbutton(master, text="Audio Only", variable=self.audio_only_var)
        self.audio_only_checkbox.pack()

        self.select_folder_button = tk.Button(master, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.folder_path_label = tk.Label(master, text=f"Folder: {self.folder_path}")
        self.folder_path_label.pack()

        self.progress_label = tk.Label(master, text="Progress:")
        self.progress_label.pack()

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progressbar = ttk.Progressbar(master, orient="horizontal", mode="determinate", style="green.Horizontal.TProgressbar")
        self.progressbar.pack()

        self.download_button = tk.Button(master, text="Download", command=self.download_playlist)
        self.download_button.pack()

        self.absolutepath_ = os.path.abspath(__file__)

    def get_playlist_size(self, playlist_url, start_video_number):
        command = [".\youtube-dl", playlist_url, "--flat-playlist"]
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            match = re.search(r"of (\d+)$", line)
            if match:
                playlist_size = int(match.group(1))
                return playlist_size
        raise Exception("Could not determine playlist size")

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_path_label.config(text=f"Folder: {self.folder_path}")

    def download_video(self, playlist_url, video_number, audio_only):
        command = [".\youtube-dl", playlist_url, "--yes-playlist", "--playlist-items", str(video_number)]
        if audio_only:
            command += ["-x", "--audio-format", "mp3"]
        if self.folder_path:
            command += ["-o", f"{self.folder_path}/%(title)s.%(ext)s"]
        subprocess.run(command)

    def download_playlist(self):
        playlist_url = self.playlist_url_entry.get()
        start_video_number = int(self.start_video_number_entry.get())
        audio_only = self.audio_only_var.get()

        playlist_size = self.get_playlist_size(playlist_url, start_video_number)
        self.progressbar.config(maximum=playlist_size-start_video_number, value=0)
        self.progress_label.config(text="Progress: 0%")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for video_number in range(start_video_number, playlist_size):
                futures.append(executor.submit(self.download_video, playlist_url, video_number, audio_only))
            for future in concurrent.futures.as_completed(futures):
                self.progressbar.step()
                self.progressbar.update()
                percent = round((self.progressbar["value"] / self.progressbar["maximum"]) * 100)
                self.progress_label.config(text=f"Progress: {percent}%")
        self.progress_label.config(text="Done!")


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()