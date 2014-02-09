from .core import Transformer
from bs4 import BeautifulSoup


class Soup(Transformer):
    def transform(self, buffer):
        soup = BeautifulSoup(buffer)
        selector = self.kwargs.get('selector')
        if selector:
            return soup.select(selector)
        else:
            return soup
