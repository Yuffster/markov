"""
Markov on a corpus.
"""
import re
import random


class MarkovChain():

    _chains = None  # {}
    _size = 1
    _key_shuffle = None  # Shuffle list of keys in chain.
    _overlap = None

    def __init__(self, size=1):
        self._size = size
        self._chains = {}
        self._key_shuffle = []

    def _get_words(self, text):
        for w in re.finditer(r"[A-Za-z!'?,\.]+", text):
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

    def _shuffle(self):
        random.shuffle(self._key_shuffle)

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

    def _get_overlapping_node(self, node, overlap):
        self._shuffle()
        node = node[overlap*-1:]
        for k in self._key_shuffle:
            if k[overlap*-1:] == node:
                return k

    def _normalize_text(self, text):
        text = text.replace("“", '"')  # Get rid of “smart” qutoes.
        text = text.replace("”", '"')
        text = text.replace("’", "'")
        text = text.replace('\n\n', ' NEWLINE ')  # Tokenize paragraph breaks.
        return text

    def _get_random_node(self):
        self._shuffle()
        for k in self._chains.keys():
            return k

    def integrate(self, text):
        text = self._normalize_text(text)
        prev = None
        for group in self._get_groups(text):
            if prev is not None:
                self._chains.setdefault(prev, {})
                pnode = self._chains[prev]
                pnode[group] = pnode.get(group, 0) + 1
            prev = group
        self._key_shuffle = list(self._chains.keys())
        self._shuffle()

    def generate(self, length=100, start=None, overlap=None):
        prev = self._get_random_node()
        for _ in range(length):
            if overlap:
                prev = self._get_overlapping_node(prev, overlap)
                if prev is None:
                    prev = self._get_random_node()
            prev = self._select_next(prev)
            out = " ".join(prev)
            out = out.replace("NEWLINE", "")
            yield out

    def trim(self, threshold):
        pops = []
        changes = False
        for k, v in self._chains.items():
            if len(v) <= threshold:
                pops.append(k)
        for k in pops:
            self._chains.pop(k)
        # Remove all the orphaned nodes.
        for k, v in self._chains.items():
            pops = []
            for j in v:
                if j not in self._chains:
                    pops.append(j)
            for orphan in pops:
                v.pop(orphan)
                changes = True
        if changes:
            self.trim(threshold)
        self._key_shuffle = list(self._chains.keys())

    def dump_stats(self, n=4):
        keys = 0
        nodes = 0
        nodes_over_n = 0
        for k, v in self._chains.items():
            keys += 1
            nodes += len(v)
            if len(v) > n:
                nodes_over_n += 1
        print("keys", keys)
        print("nodes per key", nodes/keys)
        print(
            "nodes over", n, nodes_over_n, "({}%)"
            .format((nodes_over_n/keys)*100)
        )
