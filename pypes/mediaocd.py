import re
import os
import difflib
import guessit
from . import Element, Transformer, Empty, EOF


def _regex_chain_process(s, regexes, *args, **kwargs):
    for (regex, repl) in regexes:
        s = re.subn(regex, repl, s, *args, **kwargs)[0]
    return s


def _apply_on_fields(func, d, fields):
    for field in [f for f in fields if f in d]:
        d[field] = func(d[field])


def normalize(s, regexes):
    dirname = os.path.dirname(s)
    basename, ext = os.path.splitext(s)
    return os.path.join(dirname, _regex_chain_process(basename, regexes).strip() + ext)


def nearest_match(value, match_list, cutoff=0.6):
    candidate = difflib.get_close_matches(value, match_list, cutoff=0.6)
    return candidate[0] if candidate else value


class GuessItParser(Element):
    def run(self):
        filetype = self.kwargs.get('filetype', 'autodetect')

        try:
            x = self.get()
            info = guessit.guess_file_info(x, filetype)
            self.put(info)

        except Empty:
            return False

        except EOF:
            self.finish()


class Normalizer(Transformer):
    def transform(self, value):
        regexes = self.kwargs.get('regexes', ())
        return normalize(value, regexes)


class NearestMatch(Transformer):
    def transform(self, value):
        return nearest_match(value, match_list=self.kwargs.get('match_list', ()), cutoff=self.kwargs.get('match_list', 0.6))
