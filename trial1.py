import os
import pygame
from tkinter import *
from tkinter import filedialog, ttk

# Initialize Pygame for audio playback
pygame.mixer.init()

# Create the main application window
root = Tk()
root.title("VLC-like Audio Player")
root.geometry("800x600")
root.configure(bg="#2e2e2e")  # Dark background color

# Global variables for audio
current_audio = None
is_paused = False
total_length = 0

# Function to format time in minutes:seconds
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# Function to add an audio file to the playlist
def add_audio():
    filename = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if filename:
        playlist_box.insert(END, os.path.basename(filename))  # Display in playlist box
        playlist_box.media_list.append(filename)  # Add to the media list

# Function to play selected audio file from the playlist
def play_audio():
    global current_audio, is_paused, total_length
    
    selected = playlist_box.curselection()  # Get the selected item from the playlist
    if selected:
        if not is_paused:  # If the audio is not paused, load and play the new file
            current_audio = playlist_box.media_list[selected[0]]  # Get the selected audio file path
            pygame.mixer.music.load(current_audio)  # Load the selected audio
            pygame.mixer.music.play(loops=0)  # Start playing the audio
            total_length = pygame.mixer.Sound(current_audio).get_length()  # Get the total duration of the audio
            total_time_label.config(text=f" / {format_time(total_length)}")  # Update the total time label
            update_progress_bar()  # Update the progress bar based on the audio's playback
        else:
            pygame.mixer.music.unpause()  # Resume playing the audio
            update_progress_bar()
            is_paused = False  # Reset the paused state

# Function to pause the audio
def pause_audio():
    global is_paused
    pygame.mixer.music.pause()  # Pause the currently playing audio
    is_paused = True  # Set the paused state to True

# Function to stop the audio
def stop_audio():
    pygame.mixer.music.stop()  # Stop the currently playing audio
    progress_bar['value'] = 0  # Reset the progress bar
    current_time_label.config(text="00:00")  # Reset the current time display

# Function to update the progress bar and time labels
def update_progress_bar():
    if pygame.mixer.music.get_busy():
        current_pos = pygame.mixer.music.get_pos() // 1000  # Get the current playback position in seconds
        progress_percentage = (current_pos / total_length) * 100  # Calculate the progress percentage
        progress_bar['value'] = progress_percentage  # Update the progress bar value
        current_time_label.config(text=format_time(current_pos))  # Update the current time label
        root.after(1000, update_progress_bar)  # Call this function every second
    else:
        progress_bar['value'] = 0  # Reset the progress bar
        current_time_label.config(text="00:00")  # Reset the current time label

# Playlist Box with media list
class MediaListbox(Listbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_list = []

playlist_box = MediaListbox(root, selectmode=SINGLE, width=50, height=5, bg="#3c3c3c", fg="white", selectbackground="#666666")
playlist_box.pack(pady=10)

# Control Buttons for Media
Button(root, text="➕ Add Audio", command=add_audio, bg="#4caf50", fg="white").pack(side=LEFT, padx=5)
Button(root, text="▶️ Play Audio", command=play_audio, bg="#2196f3", fg="white").pack(side=LEFT, padx=5)
Button(root, text="⏸ Pause Audio", command=pause_audio, bg="#ff9800", fg="white").pack(side=LEFT, padx=5)
Button(root, text="⏹ Stop Audio", command=stop_audio, bg="#f44336", fg="white").pack(side=LEFT, padx=5)

# Time display for media (current and total)
current_time_label = Label(root, text="00:00", bg="#2e2e2e", fg="white")
current_time_label.pack(side=LEFT)
total_time_label = Label(root, text=" / 00:00", bg="#2e2e2e", fg="white")
total_time_label.pack(side=LEFT)

# Progress Bar with seek functionality
progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
