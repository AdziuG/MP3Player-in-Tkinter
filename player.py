from tkinter import *
from tkinter import filedialog
from pathlib import Path
import pygame
from pygame import mixer
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk


class MP3Player(Tk):

    playlist = []

    def __init__(self):
        super().__init__()

        # Initialize Pygame
        pygame.init()
        mixer.init()

        self.title("MP3 Player")
        self.geometry("500x450")

        # Create main frame
        self.main_frame = Frame(self)
        self.main_frame.pack(pady=20)

        # Create Playlist Box
        self.playlist_box = Listbox(self.main_frame, bg='black', fg='green', width=60, selectbackground='green',
                                    selectforeground='black', selectmode="extended")
        self.playlist_box.grid(row=0, column=0)

        # Create volume slider frame
        self.volume_frame = LabelFrame(self.main_frame, text="Volume")
        self.volume_frame.grid(row=0, column=1)

        # Create volume slider
        self.volume_slider = ttk.Scale(self.volume_frame, from_=1, to=0, orient=VERTICAL,
                                       length=125, value=1, command=self.volume)
        self.volume_slider.pack(padx=5, pady=5)

        # Create song slider
        self.song_slider = ttk.Scale(self.main_frame, from_=0, to=100, orient=HORIZONTAL,
                                     length=360, value=0, command=self.slide)
        self.song_slider.grid(row=2, column=0, pady=20)

        # Define Button Images for Controls
        self.back_btn_img = PhotoImage(file='images/previous.png')
        self.forward_btn_img = PhotoImage(file='images/right.png')
        self.play_btn_img = PhotoImage(file='images/play-button.png')
        self.pause_btn_img = PhotoImage(file='images/pause-button.png')
        self.stop_btn_img = PhotoImage(file='images/stop.png')

        # Create Button Frame
        self.control_frame = Frame(self.main_frame)
        self.control_frame.grid(row=1, column=0)

        # Create Play/Stop and other buttons
        back_button = Button(self.control_frame,
                             image=self.back_btn_img,
                             borderwidth=0,
                             command=self.previous_song)
        back_button.grid(row=0, column=0, padx=10)

        forward_button = Button(self.control_frame,
                                image=self.forward_btn_img,
                                borderwidth=0,
                                command=self.next_song)
        forward_button.grid(row=0, column=1, padx=10)

        play_button = Button(self.control_frame,
                             image=self.play_btn_img,
                             borderwidth=0,
                             command=self.play_song)
        play_button.grid(row=0, column=2, padx=10)

        pause_button = Button(self.control_frame,
                              image=self.pause_btn_img,
                              borderwidth=0,
                              command=lambda: self.pause_song(self.is_paused))
        pause_button.grid(row=0, column=3, padx=10)

        stop_button = Button(self.control_frame,
                             image=self.stop_btn_img,
                             borderwidth=0,

                             command=self.stop_song)
        stop_button.grid(row=0, column=4, padx=10)

        # Temporary label
        self.my_label = Label(self, text='')
        self.my_label.pack(pady=20)

        # Create menu
        my_menu = Menu(self, tearoff=0)
        self.config(menu=my_menu)

        # Create add song menu dropdowns
        add_song_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label="Add Songs",
                            menu=add_song_menu)
        add_song_menu.add_command(label="Add songs", command=self.add_songs)

        # Create delete song menu dropdowns
        remove_song_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label='Remove songs', menu=remove_song_menu)
        remove_song_menu.add_command(label="Delete song from playlist", command=self.delete_songs)

        # Create paused variable
        self.is_paused = False

        # Create status bar
        self.status_bar = Label(self, text="Status bar", bd=1, relief=GROOVE, anchor=E)
        self.status_bar.pack(fill=X, side=BOTTOM, ipady=2)

        # Create stopped variable
        self.stopped = False

    # Create slide method for song positioning:
    def slide(self, x):
        # Getting song directory from playlist_box using index and playlist list
        song = self.playlist_box.get(ACTIVE)
        song_index = self.playlist_box.curselection()[0]
        self.my_label.config(text=song)

        # Load song with pygame mixer
        pygame.mixer.music.load(self.playlist[song_index].directory)
        pygame.mixer.music.play(loops=0, start=self.song_slider.get())

    # Create volume method
    def volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get(x=None))

    # Create method to deal with song time
    def play_time(self):
        # Check to see if song is stopped
        if self.stopped:
            return
        # Grab current song time
        current_time = pygame.mixer.music.get_pos() // 1000
        # Convert song time to time format
        converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
        # Getting song directory from playlist_box using index and playlist list
        self.playlist_box.get(ACTIVE)
        song_index = self.playlist_box.curselection()[0]
        # Load song with pygame mixer
        song = self.playlist[song_index].directory
        # Find current song length
        song_mut = MP3(song)
        self.song_length = song_mut.info.length

        # Convert song length to time format
        converted_song_length = time.strftime('%M:%S', time.gmtime(self.song_length))

        # Check to see if song is over
        if int(self.song_slider.get()) == int(self.song_length):
            self.next_song()
        # Check to see if song is paused
        elif self.is_paused:
            pass
        else:
            # Move slider along 1/s
            next_time = int(self.song_slider.get()) + 1
            self.song_slider.config(to=self.song_length, value=next_time)
            # Convert slider position to time format
            converted_current_time = time.strftime('%M:%S', time.gmtime(next_time))
            # Output slider
            self.status_bar.config(text=f'Time elapsed {converted_current_time} of {converted_song_length}')
        # Add current time to status bar and create loop to check time 1/s
        self.status_bar.config(text=f'Time elapsed {converted_current_time} of {converted_song_length}')
        self.status_bar.after(1000, self.play_time)

    # Create method to add songs to playlist
    def add_songs(self):
        self.song_titles = filedialog.askopenfiles(initialdir='audio/', title="Choose a song",
                                                   filetypes={("mp3 Files", "*.mp3")})
        # Depends on what user select (1 file or many files)
        for song_title in self.song_titles:
            self.playlist.append(PlaylistCreator(title=Path(song_title.name).name, directory=song_title.name))
            # Add to the end of the playlist and strip out directory structure
            self.playlist_box.insert(END, PlaylistCreator(title=Path(song_title.name).name, directory=song_title.name))

    # Create method to delete songs from playlist
    def delete_songs(self):
        # Get selected songs in playlist box (creating tuple)
        selected_element = self.playlist_box.curselection()
        # Remove songs from playlist box and playlist list
        for selected_index in selected_element:
            del self.playlist[selected_index]
            self.playlist_box.delete(selected_index)

    # Create play method
    def play_song(self):

        # Set stopped to false since a song is now playing
        self.stopped = False

        # Getting song directory from playlist_box using index and playlist list
        song = self.playlist_box.get(ACTIVE)
        song_index = self.playlist_box.curselection()[0]
        self.my_label.config(text=song)

        # Load song with pygame mixer
        pygame.mixer.music.load(self.playlist[song_index].directory)
        pygame.mixer.music.play(loops=0)

        self.play_time()

    # Create stop method
    def stop_song(self):
        # Stop the music
        pygame.mixer.music.stop()

        # Clear playlist selection and status bar
        self.playlist_box.selection_clear(ACTIVE)
        self.status_bar.config(text='')

        # Change stop variable to true
        self.stopped = True

    # Create pause method
    def pause_song(self, paused):
        self.is_paused = paused
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False

    # Create method to play next song
    def next_song(self):

        # Reset slider position and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)

        # Get current song index
        next_song = self.playlist_box.curselection()[0]
        next_song += 1

        # Grab the song title from the playlist
        self.playlist_box.get(next_song)

        # Load song with pygame mixer and add directory structure to file
        pygame.mixer.music.load(self.playlist[next_song].directory)
        pygame.mixer.music.play(loops=0)

        # Clear playlist selection
        self.playlist_box.selection_clear(0, END)

        # Move active bar to the next song
        self.playlist_box.activate(next_song)

        # Set active bar
        self.playlist_box.selection_set(next_song, last=None)

    # Create method to play next song
    def previous_song(self):

        # Reset slider position and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)

        # Get current song index
        previous_song = self.playlist_box.curselection()[0]
        previous_song -= 1

        # Grab the song title from the playlist
        self.playlist_box.get(previous_song)

        # Load song with pygame mixer and add directory structure to file
        pygame.mixer.music.load(self.playlist[previous_song].directory)
        pygame.mixer.music.play(loops=0)

        # Clear playlist selection
        self.playlist_box.selection_clear(0, END)

        # Move active bar to the previous song
        self.playlist_box.activate(previous_song)

        # Set active bar
        self.playlist_box.selection_set(previous_song, last=None)


class PlaylistCreator():
    def __init__(self, title, directory):
        self.title = title
        self.directory = directory

    def __str__(self):
        return self.title


mp3_player = MP3Player()
mp3_player.mainloop()