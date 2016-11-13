import json
from os import walk
from os.path import join


class LyricsCorpusWriter:
    corpus_file_extension = '.txt'

    def __init__(self, artist, data_dir):
        self.artist = artist
        self.data_dir = data_dir

    def write(self):
        with open(join(self.data_dir, self.artist, self.artist) + self.corpus_file_extension, 'w') as corpus_file:
            for cur, _, files in walk(join(self.data_dir, self.artist)):
                for file in files:
                    if file.endswith(self.corpus_file_extension):
                        continue
                    with open(join(cur, file), 'r') as json_data:
                        corpus_file.write(self._remove_non_ascii(json.load(json_data).get('lyrics')))
                        corpus_file.write('\n')

    def _remove_non_ascii(self, string):
        return "".join(i for i in string if ord(i) < 128)
