from app.lyrics_corpus_writer import LyricsCorpusWriter
from app.scrape_artist import ScrapeArtist

if __name__ == '__main__':
    scrape_artist = ScrapeArtist(artist_url=ScrapeArtist.AZLYRICS_ARTIST_URL)
    scrape_artist.scrape()
    LyricsCorpusWriter(scrape_artist.artist, scrape_artist.data_dir).write()
