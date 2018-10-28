import os
from urllib.parse import urljoin

from app.logging_wrapper import log_message
from app.page_loader import PageLoader
from app.scrape_song import ScrapeSong


class ScrapeArtist:
    AZLYRICS_ARTIST_URL = os.environ.get('ARTIST_URL', 'https://www.azlyrics.com/t/twentyonepilots.html')
    DATA_DIR = 'data/'

    def __init__(self, *, artist_url=AZLYRICS_ARTIST_URL, data_dir=DATA_DIR):
        self.artist_url = artist_url
        self.artist = artist_url[artist_url.rfind('/') + 1:artist_url.rfind('.')]
        self.data_dir = data_dir

    def scrape(self):
        soup = PageLoader(self.artist_url).load_soup()
        list_of_songs = soup.find(id='listAlbum').findAll(target='_blank')

        for song in list_of_songs:
            song_url = urljoin(self.artist_url, song.get('href'))
            song_info = ScrapeSong(song_url, self.artist, data_dir=self.data_dir).scrape()
            log_message(song_info['lyrics'])

        log_message('Done writing files')
