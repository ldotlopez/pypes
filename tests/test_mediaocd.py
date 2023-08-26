import unittest

from pypes import Pipeline
from pypes.elements import CustomTransformer, Debugger, SampleSrc, StoreSink
from pypes.mediaocd import GuessItParser, NearestMatch, Normalizer

NORMALIZE_REGEXES = (
    (r"(HDTV|VTV|720px?|mkvpro|x264|HQ edition)", ""),
    (r"\[Espa.+?ol castellano\]", ""),
    (r"\[www\..+?\]", ""),
    (r"(?:Cap\.)?(?P<season>\d+)(?P<episode>\d{2})", r" s\g<season>e\g<episode> "),
)
NEAREST_MATCH_LIST = ("El Mentalista", "Anatomía de grey", "American Horror Story")
# CAPITALIZE_REGEXES = mediaocd_CAPITALIZE_REGEXES


class TestMediaOCD(unittest.TestCase):
    def assertDictContainedIn(self, d, test):
        subd = {k: d[k] for k in test.keys()}
        self.assertEqual(subd, test)

    def test_normalize(self):
        inouts = (
            ("ShowWithBadNumbering710.avi", "ShowWithBadNumbering s7e10.avi"),
            (
                "Show with useless tags s1e14mkvpro.avi",
                "Show with useless tags s1e14.avi",
            ),
            ("EMentalista720p522 [www.newpct.com].mkv", "EMentalista s5e22.mkv"),
        )

        src = SampleSrc(sample=[i for (i, o) in inouts])
        normalizer = Normalizer(regexes=NORMALIZE_REGEXES)
        sink = StoreSink()

        Pipeline().connect_many(src, normalizer, sink).execute()
        self.assertEqual([o for (i, o) in inouts], sink.store)

    def test_nearest_match(self):
        inouts = (
            ("EMentalista s5e22.mkv", "El Mentalista"),
            ("AmerHoStry 7x01 Test title.avi", "American Horror Story"),
            ("BreBad s10e10.mkv", "BreBad"),
        )

        src = SampleSrc(sample=[i for (i, o) in inouts])

        guessit = GuessItParser()
        dictextract = CustomTransformer(func=lambda x: x["series"])
        nearest = NearestMatch(match_list=NEAREST_MATCH_LIST, cutoff=0.6)
        sink = StoreSink()

        Pipeline().connect_many(src, guessit, dictextract, nearest, sink).execute()
        self.assertEqual([o for (i, o) in inouts], sink.store)


if __name__ == "__main__":
    unittest.main()
