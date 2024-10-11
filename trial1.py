import os
import pygame
from tkinter import *
from tkinter import filedialog, ttk

# Initialize Pygame for audio playback
pygame.mixer.init()

# Create the main application window
root = Tk()
root.title("MY Player Audio Player")
root.geometry("600x200")  # Resize for better layout
root.configure(bg="#f0f0f0")  # Light background color like the image

# Global variables for audio
current_audio = None
is_paused = False
total_length = 0
current_pos = 0  # Track current position when paused

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

# Function to play or resume selected audio file from the playlist
def play_audio():
    global current_audio, is_paused, total_length, current_pos
    
    selected = playlist_box.curselection()  # Get the selected item from the playlist
    if selected:
        if not is_paused:  # If not paused, play the selected file
            current_audio = playlist_box.media_list[selected[0]]  # Get the selected audio file path
            pygame.mixer.music.load(current_audio)  # Load the selected audio
            pygame.mixer.music.play(loops=0)  # Start playing the audio
            total_length = pygame.mixer.Sound(current_audio).get_length()  # Get the total duration of the audio
            total_time_label.config(text=f" / {format_time(total_length)}")  # Update the total time label
            current_pos = 0  # Reset current position when a new audio file is played
            update_progress_bar()  # Start updating the progress bar
        else:
            pygame.mixer.music.unpause()  # Resume playing the audio
            is_paused = False  # Reset the paused state
            update_progress_bar()  # Resume updating the progress bar

# Function to pause the audio
def pause_audio():
    global is_paused, current_pos
    if not is_paused:  # If audio is currently playing
        pygame.mixer.music.pause()  # Pause the currently playing audio
        current_pos = pygame.mixer.music.get_pos() // 1000  # Record the current playback position in seconds
        is_paused = True  # Set the paused state to True

# Function to stop the audio
def stop_audio():
    global current_pos
    pygame.mixer.music.stop()  # Stop the currently playing audio
    progress_bar['value'] = 0  # Reset the progress bar
    current_time_label.config(text="00:00")  # Reset the current time display
    current_pos = 0  # Reset the current position

# Function to update the progress bar and time labels
def update_progress_bar():
    if pygame.mixer.music.get_busy():
        current_pos = pygame.mixer.music.get_pos() // 1000  # Get the current playback position in seconds
        progress_percentage = (current_pos / total_length) * 100  # Calculate the progress percentage
        progress_bar['value'] = progress_percentage  # Update the progress bar value
        current_time_label.config(text=format_time(current_pos))  # Update the current time label
        root.after(1000, update_progress_bar)  # Call this function every second
    elif not is_paused:
        progress_bar['value'] = 0  # Reset the progress bar
        current_time_label.config(text="00:00")  # Reset the current time label

# Function to adjust the volume based on the slider value
def set_volume(value):
    volume = int(value) / 100  # Convert slider value to percentage
    pygame.mixer.music.set_volume(volume)  # Set volume in pygame
    volume_label.config(text=f"{value}%")  # Update volume label

# Playlist Box with media list
class MediaListbox(Listbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_list = []

playlist_box = MediaListbox(root, selectmode=SINGLE, width=50, height=5, bg="#3c3c3c", fg="white", selectbackground="#666666")
playlist_box.pack(pady=10)

# Control Buttons for Media
controls_frame = Frame(root, bg="#f0f0f0")  # Frame to hold the control buttons

# Play, pause, stop, forward, backward buttons
Button(controls_frame, text="⏮", bg="#e0e0e0", fg="black", width=3).pack(side=LEFT, padx=3)  # Backward (not yet implemented)
Button(controls_frame, text="⏯", command=play_audio, bg="#e0e0e0", fg="black", width=3).pack(side=LEFT, padx=3)  # Play/resume
Button(controls_frame, text="⏸", command=pause_audio, bg="#e0e0e0", fg="black", width=3).pack(side=LEFT, padx=3)  # Pause
Button(controls_frame, text="⏹", command=stop_audio, bg="#e0e0e0", fg="black", width=3).pack(side=LEFT, padx=3)  # Stop
Button(controls_frame, text="⏭", bg="#e0e0e0", fg="black", width=3).pack(side=LEFT, padx=3)  # Forward (not yet implemented)

controls_frame.pack(side=TOP, pady=5)

# Time display for media (current and total)
time_frame = Frame(root, bg="#f0f0f0")
current_time_label = Label(time_frame, text="00:00", bg="#f0f0f0", fg="black")
current_time_label.pack(side=LEFT)
total_time_label = Label(time_frame, text=" / 00:00", bg="#f0f0f0", fg="black")
total_time_label.pack(side=LEFT)
time_frame.pack(side=TOP)

# Progress Bar (seek bar)
progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=5)

# Volume Control
volume_frame = Frame(root, bg="#f0f0f0")
volume_label = Label(volume_frame, text="85%", bg="#f0f0f0", fg="black")
volume_label.pack(side=RIGHT, padx=5)
volume_slider = Scale(volume_frame, from_=0, to=100, orient=HORIZONTAL, command=set_volume, bg="#f0f0f0")
volume_slider.set(300)  # Set default volume to 85%
volume_slider.pack(side=RIGHT)
volume_frame.pack(side=BOTTOM, pady=10)

# Add audio button
Button(root, text="➕ Add Audio", command=add_audio, bg="#4caf50", fg="white").pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
