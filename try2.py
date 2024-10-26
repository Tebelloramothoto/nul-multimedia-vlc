##Author
##Maime P. 202000484
##Makhosane M.A. 202003231
##Ramothoto T 202002687

import os
import cv2
import pygame
import numpy as np
from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip

# Initialize Pygame for audio playback
pygame.mixer.init()

# Create the main application window
root = Tk()
root.title("VLC-like Media Player")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Global variables
current_media = None
cap = None
is_paused = True
total_length = 0
current_pos = 0
is_video = False
playlist = []
current_index = 0

# Function to format time in minutes:seconds
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# Function to open a media file
def open_media():
    global current_media, cap, total_length, is_video, playlist
    filename = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp3 *.mp4 *.avi *.mkv *.mov")])
    if filename:
        playlist.append(filename)
        playlist_box.insert(END, os.path.basename(filename))
        if not current_media:
            play_media(len(playlist) - 1)

# Function to play or resume media
def play_media(index=None, seek_position=None):
    global current_media, cap, is_paused, total_length, current_pos, is_video, current_index, temp_audio_file

    if index is not None:
        current_index = index

    if current_index < len(playlist):
        current_media = playlist[current_index]
        _, file_extension = os.path.splitext(current_media)
        is_video = file_extension.lower() in ['.mp4', '.avi', '.mkv', '.mov']

        if is_video:
            # Handle video using OpenCV
            cap = cv2.VideoCapture(current_media)
            total_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            
            # Load the audio track using moviepy
            video_clip = VideoFileClip(current_media)
            video_audio = video_clip.audio
            
            # Extract audio and save it temporarily
            temp_audio_file = "temp_audio.mp3"
            video_audio.write_audiofile(temp_audio_file)
            
            # Load and play the audio using pygame
            pygame.mixer.music.load(temp_audio_file)
            pygame.mixer.music.set_volume(volume_scale.get() / 100)  # Set initial audio volume
            pygame.mixer.music.play()

        else:
            # Handle audio files directly with Pygame
            pygame.mixer.music.load(current_media)
            pygame.mixer.music.set_volume(volume_scale.get() / 100)  # Set initial audio volume
            total_length = pygame.mixer.Sound(current_media).get_length()

        total_time_label.config(text=f" / {format_time(total_length)}")

        if seek_position is not None and 0 <= seek_position <= total_length:
            if is_video:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(seek_position * cap.get(cv2.CAP_PROP_FPS)))
                pygame.mixer.music.play(start=seek_position)  # Sync audio with the seek position
            else:
                pygame.mixer.music.play(start=seek_position)
        else:
            if is_video:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                pygame.mixer.music.play()  # Play the audio from the beginning
            else:
                pygame.mixer.music.play()

        is_paused = False
        current_pos = seek_position if seek_position is not None else 0
        update_progress()
        if is_video:
            show_frame()
        playlist_box.selection_clear(0, END)
        playlist_box.selection_set(current_index)
        playlist_box.see(current_index)
        update_current_media_label()
        play_button.config(text="Pause")


# Function to pause media
def pause_media():
    global is_paused
    if not is_paused:
        if is_video:
            # Pause the video by simply not reading more frames
            is_paused = True
            pygame.mixer.music.pause()  # Pause the audio
            play_button.config(text="Play")
        else:
            pygame.mixer.music.pause()  # Pause the audio
            is_paused = True
            play_button.config(text="Play")
    else:
        if is_video:
            is_paused = False
            pygame.mixer.music.unpause()  # Resume the audio
            show_frame()  # Resume video playback by continuing to show frames
            play_button.config(text="Pause")
        else:
            pygame.mixer.music.unpause()  # Resume audio
            is_paused = False
            play_button.config(text="Pause")
# Function to stop media
def stop_media():
    global is_paused, current_pos
    if is_video:
        if cap:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        pygame.mixer.music.stop()
    is_paused = True
    current_pos = 0
    progress_var.set(0)
    current_time_label.config(text="00:00")
    video_label.config(image="")
    play_button.config(text="Play")

# Function to show video frames
def show_frame():
    global cap, current_pos, is_paused
    if cap is not None and not is_paused:
        # Calculate the current audio time and sync video frame
        audio_pos = pygame.mixer.music.get_pos() / 1000  # Audio position in seconds
        cap.set(cv2.CAP_PROP_POS_MSEC, audio_pos * 1000)  # Set video position based on audio time

        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((640, 480), Image.LANCZOS)  # Fixed size for video
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.config(image=imgtk)
            root.after(10, show_frame)
        else:
            next_media()

# Function to update the progress
def update_progress():
    global current_pos, total_length, is_paused
    if not is_paused:
        if is_video:
            if cap:
                current_pos = cap.get(cv2.CAP_PROP_POS_FRAMES) / cap.get(cv2.CAP_PROP_FPS)
        else:
            current_pos = pygame.mixer.music.get_pos() / 1000
        progress_var.set(min(current_pos / total_length * 100, 100))
        current_time_label.config(text=format_time(current_pos))
    root.after(100, update_progress)

# Function to seek in media
def seek(event):
    global current_pos
    seek_time = (event.x / progress_bar.winfo_width()) * total_length
    play_media(seek_position=seek_time)

# Function to adjust volume
def set_volume(value):
    volume = float(value) / 100  # Use float instead of int
    pygame.mixer.music.set_volume(volume)

# Function to play next media
def next_media():
    global current_index
    if current_index < len(playlist) - 1:
        current_index += 1
        play_media(current_index)
    else:
        stop_media()

# Function to play previous media
def prev_media():
    global current_index
    if current_index > 0:
        current_index -= 1
        play_media(current_index)

# Function to update current media label
def update_current_media_label():
    if current_media:
        current_media_label.config(text=os.path.basename(current_media))
    else:
        current_media_label.config(text="No media selected")

# Function to remove selected item from playlist
def remove_from_playlist():
    global current_index, playlist
    selection = playlist_box.curselection()
    if selection:
        index = selection[0]
        playlist_box.delete(index)
        del playlist[index]
        if index == current_index:
            stop_media()
            if playlist:
                play_media(min(index, len(playlist) - 1))
        elif index < current_index:
            current_index -= 1

# Create UI elements
video_frame = Frame(root, bg="black", width=640, height=480)
video_frame.pack(padx=10, pady=10)
video_frame.pack_propagate(False)  # Prevent the frame from resizing

video_label = Label(video_frame, bg="black")
video_label.pack(expand=True, fill=BOTH)

control_frame = Frame(root, bg="#f0f0f0")
control_frame.pack(fill=X, padx=10, pady=5)

current_time_label = Label(control_frame, text="00:00", bg="#f0f0f0")
current_time_label.pack(side=LEFT)

total_time_label = Label(control_frame, text=" / 00:00", bg="#f0f0f0")
total_time_label.pack(side=LEFT)

progress_var = DoubleVar()
progress_bar = ttk.Progressbar(control_frame, variable=progress_var, maximum=100, length=400)
progress_bar.pack(side=LEFT, padx=10, fill=X, expand=True)
progress_bar.bind("<Button-1>", seek)

volume_label = Label(control_frame, text="Volume", bg="#f0f0f0")
volume_label.pack(side=LEFT, padx=(10, 0))

volume_scale = ttk.Scale(control_frame, from_=0, to=100, orient=HORIZONTAL, command=set_volume, length=100)
volume_scale.set(50)  # Default volume
volume_scale.pack(side=LEFT)

button_frame = Frame(root, bg="#f0f0f0")
button_frame.pack(fill=X, padx=10, pady=5)

open_button = ttk.Button(button_frame, text="Open", command=open_media)
open_button.pack(side=LEFT, padx=5)

play_button = ttk.Button(button_frame, text="Play", command=pause_media)
play_button.pack(side=LEFT, padx=5)

stop_button = ttk.Button(button_frame, text="Stop", command=stop_media)
stop_button.pack(side=LEFT, padx=5)

prev_button = ttk.Button(button_frame, text="Previous", command=prev_media)
prev_button.pack(side=LEFT, padx=5)

next_button = ttk.Button(button_frame, text="Next", command=next_media)
next_button.pack(side=LEFT, padx=5)

remove_button = ttk.Button(button_frame, text="Remove", command=remove_from_playlist)
remove_button.pack(side=LEFT, padx=5)

current_media_label = Label(root, text="No media selected", bg="#f0f0f0")
current_media_label.pack(pady=5)

playlist_frame = Frame(root)
playlist_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

playlist_box = Listbox(playlist_frame, selectmode=SINGLE, bg="#ffffff", fg="black")
playlist_box.pack(fill=BOTH, expand=True, side=LEFT)

scrollbar = ttk.Scrollbar(playlist_frame, orient=VERTICAL, command=playlist_box.yview)
scrollbar.pack(side=RIGHT, fill=Y)
playlist_box.config(yscrollcommand=scrollbar.set)

playlist_box.bind('<Double-1>', lambda event: play_media(playlist_box.curselection()[0]))

# Start the application
update_progress()
root.mainloop()
