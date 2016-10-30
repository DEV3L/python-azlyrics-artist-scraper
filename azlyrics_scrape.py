import json
import time
import urllib.request
from hashlib import sha1
from os import makedirs
from os.path import join, isdir, exists
from random import randint
from urllib.parse import urljoin

import bs4

AZLYRICS_URL = 'http://www.azlyrics.com/t/taylorswift.html'
CACHE_DIR = 'html/'


class LyricsWalker:
    """
    Class for lyric gathering. Currently for AZ Lyrics, but can be adapted into
    base case with varying scraping functions.
    """

    @classmethod
    def get_song_info(cls, url):
        """
        Grabs lyrics from URL and return plain text lyrics.
        Lyrics are located at /html/body/div[3]/div/div[2]/div[6]
        """
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
            print(('Error parsing: %s' % url))
            print(e)
            return None

        album_str = album.replace(' ', '_').replace(':', '') if album else None
        title_str = title.replace(' ', '_').replace(':', '').replace("'", '').replace('/', '').replace(',', '').replace(
                '?', '')

        entry_info = {
            'lyrics': lyrics,
            'album': album,
            'year': year,
            'title': title
        }

        if album is not None:
            output_file_dir = 'data/%s_%s/' % (album_str, year)
        else:
            output_file_dir = 'data/noalbum/'

        if not isdir(output_file_dir):
            makedirs(output_file_dir)

        output_filename = join(output_file_dir, '%s.json' % title_str)
        f = open(output_filename, 'w')
        json.dump(str(entry_info), f, sort_keys=1, indent=2)
        f.close()

        print(('Parsed %s' % title))
        return entry_info

    @classmethod
    def get_lyrics(cls, soup):
        """
        Method for extracting lyrics from BeautifulSoup. Relies on the fact that
        lyrics are very long instead of relying on consistent formatting from AZ Lyrics.
        """
        all_div = soup.findAll('div')
        all_text = [i.text for i in all_div if i.attrs.get('class') and 'main-page' in i.attrs.get('class')][0].strip()
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
        time.sleep(randint(15, 30))
        print(('Read %s' % url))
        full_html = urlobject.read()

        if html:
            return bs4.BeautifulSoup(full_html, 'html.parser'), full_html
        return bs4.BeautifulSoup(full_html, 'html.parser')

    @classmethod
    def url_to_filename(cls, url):
        """
        Make a URL into a file name, using SHA1 hashes.
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
            print(('Stored locally %s' % url))

    @classmethod
    def load_local(cls, url):
        local_path = cls.url_to_filename(url)
        if not exists(local_path):
            return None
        with open(local_path, 'rb') as f:
            print(('Loaded locally: %s' % url))
            return f.read()

    @classmethod
    def ascii_encoder(cls, data):
        ascii_encode = lambda x: x.decode('ascii') if x is not None else None
        return dict(list(map(ascii_encode, pair)) for pair in list(data.items()))

    @classmethod
    def walk_homepage(cls, home_url, *, output_dir=''):
        soup = cls.get_soup_from_url(home_url)
        song_lst = soup.find(id='listAlbum').findAll(target='_blank')

        had_previous = False
        filename = join(output_dir, 'az_lyrics.json')
        with open(filename, 'w') as f:
            for song in song_lst:
                f.write(',' if had_previous else '[')
                had_previous = True
                song_url = urljoin(home_url, song.get('href'))
                song_info = cls.get_song_info(song_url)
                print(song_info['lyrics'])
                json.dump(song_info, f)
            f.write(']')
        print('Wrote all songs to json!')


if __name__ == '__main__':
    LyricsWalker.walk_homepage(AZLYRICS_URL)
