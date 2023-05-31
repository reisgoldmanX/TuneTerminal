import librosa
import sounddevice as sd
import time
import os
from tinytag import TinyTag

class Music:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.metadata = self.extract_metadata()
        
    def extract_metadata(self):
        tag = TinyTag.get(self.file_path)
        metadata = {
            "artist": tag.artist,
            "title": tag.title,
            "album": tag.album,
            "duration": tag.duration
        }
        return metadata
    
    @property
    def artist(self):
        return self.metadata.get("artist", "")

    @property
    def title(self):
        if self.metadata.get("title", "") is None:
            return os.path.basename(self.file_path).split(".")[0]
        return self.metadata.get("title", "")

    @property
    def album(self):
        return self.metadata.get("album", "")

    @property
    def duration(self):
        return self.metadata.get("duration", 0)

        
        
class PlayList:
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        self.music_files = self.playlist()
        self.current = 0
    
    @property
    def current_song(self):
        return self.music_files[self.current]
        
    def playlist(self) -> list[Music]:
        audio_extensions = ['.mp3', '.wav', '.flac']
        audio_files = []

        # Traverse the directory and find audio files
        for root, dirs, files in os.walk(self.dir_path):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in audio_extensions:
                    audio_files.append(Music(os.path.join(root, file)))

        return audio_files

class MusicPlayer:
    def __init__(self, dir_path: str):
        self.playlist = PlayList(dir_path)
        self.current_song = self.playlist.current_song
        self.is_playing = False
        self.current_time = 0
        self.volume = 1.0
        self.load_song()

    def load_song(self):
        self.file_path = self.current_song.file_path
        self.y, self.sr = librosa.load(self.file_path, sr=None)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        self.play()

    def next(self):
        self.reset()
        self.playlist.current += 1
        if self.playlist.current >= len(self.playlist.music_files):
            self.playlist.current = 0
        self.current_song = self.playlist.current_song
        self.load_song()

    def prev(self):
        self.reset()
        self.playlist.current -= 1
        if self.playlist.current < 0:
            self.playlist.current = len(self.playlist.music_files) - 1
        self.current_song = self.playlist.current_song
        self.load_song()

    def play(self):
        if not self.is_playing:
            start_sample = int(self.current_time * self.sr)
            sd.play(self.y[start_sample:], self.sr)
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            self.current_time += sd.get_stream().time
            sd.stop()
            self.is_playing = False

    def reset(self):
        sd.stop()
        self.current_time = 0
        self.is_playing = False

    def seek(self, position):
            self.stop()
            self.current_time = position
            self.play()
            

    def set_volume(self, volume):
        self.volume = volume
        if self.is_playing:
            sd.set_volume(volume)


    def display_current_time(self) -> tuple:
        """
        Return: Tuple[Minutes, Seconds]
        """
        

        self.current_time = sd.get_stream().time
        print(sd.get_stream().time)
        
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        time_string = (f"{minutes:02d}", f"{seconds:02d}")
        return time_string


    def get_duration(self) -> tuple:
        """
        return: Tuple[Minutes, Seconds]
        """
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return (f"{minutes:02d}", f"{seconds:02d}")


    
a = MusicPlayer(r"D:\Developer\\Experiments\\Python\\Old\\old_projects\self_mp3\\Music")

a.play()
print(a.playlist.current_song.title)
time.sleep(10)
a.next()
print(a.playlist.current_song.title)
time.sleep(40)