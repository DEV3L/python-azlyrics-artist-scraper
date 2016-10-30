import urllib.request

import requests as request
from bs4 import BeautifulSoup

from logging_wrapper import get_logger, log_message, log_exception


class ProxyRequester:
    def __init__(self, proxy_scraper):
        self.proxy_scrapper = proxy_scraper

    def get(self, url):
        for proxy in self.proxy_scrapper.proxies:
            urllib.request.getproxies()
            try:
                page = request.get(url, proxies={"http": proxy})
                if page.status_code != 200:
                    log_message(
                            'GET ''{}'' with proxy: {}, returned status_code {}'.format(url, proxy, page.status_code))
                    continue
                log_message('GET ''{}'' with proxy: {}'.format(url, proxy))
                return page
            except Exception:
                log_exception('GET failed to load ''{}'' with proxy: {}'.format(url, proxy))


class ProxyScraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)",
        "Referer": "http://example.com"
    }

    PROXY_LIST_URL = 'http://www.xroxy.com/proxylist.php?port=Standard&type=All_http&ssl=&country=&latency=&reliability=9000&sort=reliability&desc=true&pnum={}#table'

    def __init__(self, proxylist_url=PROXY_LIST_URL):
        self.proxies = []
        self.gather_proxies(proxylist_url)
        self.logger = get_logger()

    def gather_proxies(self, proxylist_url):
        page = 0

        while True:
            soup = BeautifulSoup(request.get(proxylist_url.format(page), headers=self.HEADERS).content)
            soup.prettify()
            page += 1

            links = soup.find_all('a', title="Configure FoxyProxy in single click")

            if not links:
                break

            for link in links:
                # this could probably be done more gracefully with a few good regular expressions
                href = link.get('href')
                ip = href.rsplit('&port', 1)[:1][0].replace('proxy:name=XROXY proxy&host=', '')
                _ = href.rsplit('&notes', 1)[:1][0].replace('proxy:name=XROXY proxy&host=' + ip + '&port=', '')
                port = _[:_.index('¬')]
                proxy = 'http://{}:{}'.format(ip, port)
                log_message('Adding proxy: {}'.format(proxy))
                self.proxies.append(proxy)


if __name__ == '__main__':
    proxy_scraper = ProxyScraper()
    proxy_requestor = ProxyRequester(proxy_scraper)
    page = proxy_requestor.get('http://www.azlyrics.com/t/taylorswift.html/')
    print(page.content)
