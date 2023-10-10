#!/usr/bin/env python3.9
import re
import guessit


class MyGuessit:

    def __init__(self, title: str):
        title = title.lower()

        draft = title.replace("\n", ' ')
        draft = draft.replace("-", ' ')
        draft = re.sub(r'\sby.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\s#.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\sepisod.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\sspecial.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\sstagion.*', '', draft, re.IGNORECASE)
        draft = re.sub(r' \scorto.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\sprima tv.*', '', draft, re.IGNORECASE)
        draft = re.sub(r'\sversione.*', '', draft, re.IGNORECASE)
        self.guess = guessit.guessit(draft)

    @property
    def title(self):
        return ''.join(map(str, self.guess.get('title', '')))

    @property
    def series(self):
        return ''.join(map(str, self.guess.get('series', '')))

    @property
    def alternative_title(self):
        return ''.join(map(str, self.guess.get('alternative_title', '')))

    @property
    def year(self):
        return ''.join(map(str, str(self.guess.get('year', ''))))

    @property
    def release_group(self):
        return self.guess.get('release_group', '')

    def __str__(self):
        return ' '.join([self.title, self.series, self.alternative_title])
