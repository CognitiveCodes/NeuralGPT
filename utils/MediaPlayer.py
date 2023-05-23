import vlc

class MediaPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def play_media(self, media_path):
        media = self.instance.media_new(media_path)
        self.player.set_media(media)
        self.player.play()

    def stop_media(self):
        self.player.stop()