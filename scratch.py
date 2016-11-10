from markov import MarkovChain

m = MarkovChain(size=3)
m.integrate(open('ignore/corpus.txt').read())
print('Vocab length', len(m._chains.keys()))
print(" ".join(list(m.generate(100))))