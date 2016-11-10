import time
import urllib.request
from hashlib import sha1
from os import makedirs
from os.path import join, isdir, exists
from random import randint

import bs4

from app.logging_wrapper import log_message


class PageLoader:
    CACHE_DIR = 'html/'

    def __init__(self, url, *, cache_dir=CACHE_DIR):
        self.url = url
        self.cache_dir = cache_dir

    def load_soup(self):
        file_bytes = self._load_local(self.url)
        if file_bytes:
            soup = bs4.BeautifulSoup(file_bytes, 'html.parser')
        else:
            soup, html = self._get_soup_from_url()
            self._store_local(html)

        return soup

    def _load_local(self, url):
        file_bytes = None
        local_path = self._url_to_filename()
        if not exists(local_path):
            return file_bytes
        with open(local_path, 'rb') as file:
            log_message('Loaded locally: %s' % self.url)
            file_bytes = file.read()

        return file_bytes

    def _store_local(self, content):
        if not isdir(self.cache_dir):
            makedirs(self.cache_dir)

        local_path = self._url_to_filename()
        with open(local_path, 'wb') as file:
            file.write(content)
            log_message('Stored locally %s' % self.url)

    def _url_to_filename(self):
        """
        SHA1 hash URL as a file name
        """
        hash_file = sha1(str.encode(self.url)).hexdigest() + '.html'
        return join(self.cache_dir, hash_file)

    def _get_soup_from_url(self):
        urlobject = urllib.request.urlopen(self.url)

        # AZLyrics is eagerly blocks IPs
        time.sleep(randint(20, 30))

        log_message('Read %s' % self.url)
        full_html = urlobject.read()

        return bs4.BeautifulSoup(full_html, 'html.parser'), full_html
