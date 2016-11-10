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
            album_info = soup.find('div', {'class': 'album-panel'})
            if album_info:
                album_text = album_info.text.strip()
                album = album_text.split('"')[1]
                year = album_text.split('(')[1][:-1]
            else:
                album, year = None, None
            title = soup.title.text.split(' - ')[-1]
            lyrics = self.get_lyrics(soup)
        except Exception as e:
            log_exception('Error parsing: %s' % self.url)
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
        output_file_dir = '%s%s/%s_%s/' % (self.data_dir, self.artist, year, album_str)

        if not isdir(output_file_dir):
            makedirs(output_file_dir)

        output_filename = join(output_file_dir, '%s.json' % title_str)

        with open(output_filename, 'w') as write_file:
            json.dump(entry_info, write_file)

        log_message('Parsed %s' % title)
        return entry_info

    def get_lyrics(self, soup):
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
