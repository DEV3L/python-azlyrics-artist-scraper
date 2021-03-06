import json
from os import makedirs
from os.path import join, isdir

from app.logging_wrapper import log_message, log_exception
from app.page_loader import PageLoader


class ScrapeSong:
    def __init__(self, url, artist, *, data_dir=None):
        from app.scrape_artist import ScrapeArtist
        data_dir = data_dir if data_dir else ScrapeArtist.DATA_DIR
        self.url = url
        self.artist = artist
        self.data_dir = data_dir

    def scrape(self):
        soup = PageLoader(self.url).load_soup()

        try:
            album_info = soup.find('div', {'class': 'songlist-panel'})
            album_text = album_info.text.strip() if album_info else None

            if album_text and '"' in album_text:
                album = album_text.split('"')[1]
                year = album_text.split('(')[1][:-1]

                if year:
                    year = year.split(')')[0]
            else:
                album, year = None, None
            title = soup.title.text.split(' - ')[-1].replace(' | AZLyrics.com', '')
            if 'Lovely' in title:
                print()
            if 'Fake You Out' in title:
                print()
            lyrics = self.get_lyrics(soup)
        except Exception as e:
            log_exception(f'Error parsing: {self.url}')
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

        album_str = album_str if album_str else 'no_album'
        output_file_dir = f'{self.data_dir}{self.artist}/{year}_{album_str}/'

        if not isdir(output_file_dir):
            makedirs(output_file_dir)

        output_filename = join(output_file_dir, f'{title_str}.json')

        with open(output_filename, 'w') as write_file:
            json.dump(entry_info, write_file)

        log_message(f'Parsed {title}')
        return entry_info

    def get_lyrics(self, soup):
        all_div = soup.findAll('div')
        all_text = [div.text for div in all_div
                    if div.attrs.get('class') and 'main-page' in div.attrs.get('class')][0].strip()

        stripped_lines = [line.strip() for line in all_text.split('\n') if line.strip()]

        lyrics = []

        _lyrics = stripped_lines[3:]
        for line in _lyrics:
            if line.startswith('if  (') or line.startswith('if ('):
                break
            lyrics.append(line)

        return "\n".join(lyrics)
