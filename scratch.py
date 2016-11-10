from markov import MarkovChain

m = MarkovChain(size=2)
m.integrate(open('ignore/corpus.txt').read())

print(" ".join(list(m.generate(100, overlap=None))))
m.dump_stats(n=1)

m.trim(1)

m.dump_stats(n=1)

print(" ".join(list(m.generate(100, overlap=None))))