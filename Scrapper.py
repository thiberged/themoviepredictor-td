import requests
from bs4 import BeautifulSoup

class Scrapper:

    def __init__(self,url):
        self.url = url

    def scrap(self):
        r = requests.get(self.url)
        self.data = BeautifulSoup(r.text, 'html.parser')