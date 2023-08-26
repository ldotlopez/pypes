from bs4 import BeautifulSoup

from .core import Transformer


class Soup(Transformer):
    def transform(self, buffer):
        soup = BeautifulSoup(buffer)
        selector = self.kwargs.get("selector")
        if selector:
            return soup.select(selector)
        else:
            return soup
