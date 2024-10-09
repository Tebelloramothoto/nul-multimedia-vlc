import os
import pygame
from tkinter import *
from tkinter import filedialog
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Initialize Pygame for audio playback
pygame.mixer.init()

# Create the main application window
root = Tk()
root.title("Multimedia Player")
root.geometry("500x500")

# Global variables for audio
audio_playlist = []
current_audio = None
is_paused = False

# Function to add an audio file to the playlist
def add_audio():
    filename = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if filename:
        audio_playlist.append(filename)
        playlist_box.insert(END, os.path.basename(filename))

# Function to play selected audio file from the playlist
def play_audio():
    global current_audio, is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
    else:
        selected = playlist_box.curselection()
        if selected:
            current_audio = audio_playlist[selected[0]]
            pygame.mixer.music.load(current_audio)
            pygame.mixer.music.play()

# Function to pause the audio
def pause_audio():
    global is_paused
    pygame.mixer.music.pause()
    is_paused = True

# Function to stop the audio
def stop_audio():
    pygame.mixer.music.stop()

# Function to remove selected audio from the playlist
def remove_audio():
    selected = playlist_box.curselection()
    if selected:
        playlist_box.delete(selected)
        del audio_playlist[selected[0]]

# GUI for Audio Player
audio_frame = LabelFrame(root, text="Audio Player", padx=10, pady=10)
audio_frame.pack(padx=10, pady=10)

playlist_box = Listbox(audio_frame, selectmode=SINGLE, width=50, height=5)
playlist_box.pack()

Button(audio_frame, text="Add Audio", command=add_audio).pack(side=LEFT)
Button(audio_frame, text="Play", command=play_audio).pack(side=LEFT)
Button(audio_frame, text="Pause", command=pause_audio).pack(side=LEFT)
Button(audio_frame, text="Stop", command=stop_audio).pack(side=LEFT)
Button(audio_frame, text="Remove", command=remove_audio).pack(side=LEFT)

# Global variables for video
video_player = None

# Function to play the selected video
def play_video():
    filename = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if filename:
        clip = VideoFileClip(filename)
        clip.preview()

# GUI for Video Player
video_frame = LabelFrame(root, text="Video Player", padx=10, pady=10)
video_frame.pack(padx=10, pady=10)

Button(video_frame, text="Upload & Play Video", command=play_video).pack()

# Start the Tkinter event loop
root.mainloop()
