"""
Markov on a corpus.
"""
import re
import random


class MarkovChain():

    _chains = {}  # None
    _size = 1

    def __init__(self, size=1):
        self._size = size

    def _get_words(self, text):
        text = text.replace("“", '"')
        text = text.replace("”", '"')
        text = text.replace("’", "'")
        text = text.replace('\n\n', ' NEWLINE ')  # Tokenize paragraph breaks.
        for w in re.finditer(r"[A-Za-z0-9!\-':\)\(\"?,\.]+", text):
            yield w.group(0)

    def _get_groups(self, text):
        word_gen = self._get_words(text)
        while True:
            c = []
            try:
                for _ in range(self._size):
                    c.append(next(word_gen))
                yield tuple(c)
            except StopIteration:
                break

    def _select_next(self, key):
        probs = 0
        p_range = {}
        for k, prob in self._chains[key].items():
            probs += prob
            p_range[probs] = k
        v = random.randint(0, probs)
        for p, node in sorted(p_range.items()):
            if p >= v:
                return node

    def integrate(self, text):
        text = text.lower()
        prev = None
        for group in self._get_groups(text):
            if prev is not None:
                self._chains.setdefault(prev, {})
                self._chains[prev][group] = self._chains[prev].get(group, 0) + 1
            prev = group
    
    def generate(self, length=100, start=None):
        for k in self._chains.keys():
            prev = k
            break
        for _ in range(length):
            prev = self._select_next(prev)
            yield " ".join(prev).replace('NEWLINE', "")
