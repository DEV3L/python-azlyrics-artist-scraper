import json
import time
import urllib.request
from hashlib import sha1
from os import makedirs
from os.path import join, isdir, exists
from random import randint
from urllib.parse import urljoin

import bs4

from logging_wrapper import log_message, log_exception

AZLYRICS_ARTIST_URL = 'http://www.azlyrics.com/t/taylorswift.html'
CACHE_DIR = 'html/'


class AZLyricsScrape:
    def __init__(self, *, artist_url=AZLYRICS_ARTIST_URL):
        self.artist_url=artist_url
        self.artist=artist_url[artist_url.rfind('/')+1:artist_url.rfind('.')]
        pass

    @classmethod
    def get_song_info(cls, url, artist):
        if cls.load_local(url):
            soup = bs4.BeautifulSoup(cls.load_local(url), 'html.parser')
        else:
            soup, html = cls.get_soup_from_url(url, html=True)
            cls.store_local(url, html)

        try:
            album_info = soup.find('div', {'class': 'album-panel'})
            if album_info:
                album_text = album_info.text.strip()
                album = album_text.split('"')[1]
                year = album_text.split('(')[1][:-1]
            else:
                album, year = None, None
            title = soup.title.text.split(' - ')[-1]
            lyrics = cls.get_lyrics(soup)
        except Exception as e:
            log_exception('Error parsing: %s' % url)
            log_exception(e)
            return None

        album_str = album.replace(' ', '_').replace(':', '') if album else None
        title_str = title.replace(' ', '_').replace(':', '').replace("'", '') \
            .replace('/', '').replace(',', '').replace('?', '')

        entry_info = {
            'lyrics': lyrics,
            'album': album,
            'year': year,
            'title': title
        }

        if album is not None:
            output_file_dir = 'data/%s/%s_%s/' % (artist, year, album_str)
        else:
            output_file_dir = 'data/%s/no_album/' % (artist)

        if not isdir(output_file_dir):
            makedirs(output_file_dir)

        output_filename = join(output_file_dir, '%s.json' % title_str)
        write_file = open(output_filename, 'w')
        json.dump(str(entry_info), write_file, sort_keys=1, indent=2)
        write_file.close()

        log_message('Parsed %s' % title)
        return entry_info

    @classmethod
    def get_lyrics(cls, soup):
        all_div = soup.findAll('div')
        all_text = [i.text for i in all_div
                    if i.attrs.get('class') and 'main-page'
                    in i.attrs.get('class')][0].strip()
        return_text = ''

        for line in [i for i in all_text.split('\n') if i.strip()][5:]:
            if line.startswith('if  ('):
                break
            return_text += line + '\n'

        return return_text.strip()

    @classmethod
    def get_soup_from_url(cls, url, html=False):
        urlobject = urllib.request.urlopen(url)

        # AZLyrics is eagerly blocks IPs
        time.sleep(randint(20, 30))
        log_message('Read %s' % url)
        full_html = urlobject.read()

        if html:
            return bs4.BeautifulSoup(full_html, 'html.parser'), full_html
        return bs4.BeautifulSoup(full_html, 'html.parser')

    @classmethod
    def url_to_filename(cls, url):
        """
        SHA1 hash URL as a file name
        """
        hash_file = sha1(str.encode(url)).hexdigest() + '.html'
        return join(CACHE_DIR, hash_file)

    @classmethod
    def store_local(cls, url, content):
        if not isdir(CACHE_DIR):
            makedirs(CACHE_DIR)

        local_path = cls.url_to_filename(url)
        with open(local_path, 'wb') as f:
            f.write(content)
            log_message('Stored locally %s' % url)

    @classmethod
    def load_local(cls, url):
        local_path = cls.url_to_filename(url)
        if not exists(local_path):
            return None
        with open(local_path, 'rb') as f:
            log_message('Loaded locally: %s' % url)
            return f.read()

    def scrape_artist_page(self):
        soup = self.get_soup_from_url(self.artist_url)
        list_of_songs = soup.find(id='listAlbum').findAll(target='_blank')

        had_previous = False
        filename = '%s_%s.%s' % ('az_lyrics', self.artist, '.json')

        with open(filename, 'w') as f:
            for song in list_of_songs:
                f.write(',' if had_previous else '[')
                had_previous = True
                song_url = urljoin(self.artist_url, song.get('href'))
                song_info = self.get_song_info(song_url, self.artist)
                log_message(song_info['lyrics'])
                json.dump(song_info, f)
            f.write(']')

        log_message('Done writing files')


if __name__ == '__main__':
    azlyrics_scrape = AZLyricsScrape(artist_url=AZLYRICS_ARTIST_URL)
    azlyrics_scrape.scrape_artist_page()
    # AZLyricsScrape.scrape_artist_page(AZLYRICS_ARTIST_URL)
