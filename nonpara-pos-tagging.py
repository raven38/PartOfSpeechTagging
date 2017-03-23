#!/usr/bin/env python
"""
This program is pos tagging by bayesian HMM
"""
import numpy as np
from numpy.random import rand, randint

c = {}
alpha = 0.01
N = 10
S = 21
xcorpus = []
ycorpus = []

def P(a, b):
    if a == S:
        return alpha / (c.get(b, 0) + alpha)
    return c.get((b,a), 0) / (c.get(b, 0) + alpha)

def count(key, value):
    if key in c:
        c[key] += value
    else:
        c[key] = 1

def sampleOne(probs):
    z = 0
    for k, v in probs.items():
        z += v
    remaining = rand()*z
    for k, v in probs.items():
        remaining -= v
        if remaining <= 0:
            return k
    print('sampleOne error')
    return -1

def sampleTag(i, j):
    count((ycorpus[i][j-1], ycorpus[i][j]), -1)
    count((ycorpus[i][j], ycorpus[i][j+1]), -1)
    count((ycorpus[i][j], xcorpus[i][j]), -1)

    p = {}
    for tag in range(S):
        if (ycorpus[i][j-1], tag) in c and (tag, ycorpus[i][j+1]) in c and (tag, xcorpus[i][j]) in c:
            p[tag] = P(tag, ycorpus[i][j-1]) * P(ycorpus[i][j+1], tag) * P(xcorpus[i][j], tag)
    p[S] = P(S, ycorpus[i][j-1]) * P(ycorpus[i][j+1], S) * P(xcorpus[i][j], S)

    ycorpus[i][j] = sampleOne(p)

    count((ycorpus[i][j-1], ycorpus[i][j]), 1)
    count((ycorpus[i][j], ycorpus[i][j+1]), 1)
    count((ycorpus[i][j], xcorpus[i][j]), 1)

def sampleCorpus():
    for i in range(len(xcorpus)):
        for j in range(1, len(xcorpus[i])-1):
            sampleTag(i, j)

def init(infile):
    with open(infile, 'r') as f:
        first_line = 1
        for line in f:
            X = ['<s>'] + line[:-1].split(' ') + ['<s>']
            Y = list(randint(0, S, len(X)))
            for i in range(1, len(X)-1):
                count((Y[i-1], Y[i]), 1)
                count((Y[i], Y[i+1]), 1)
                count((Y[i], X[i]), 1)
            for y in Y:
                count(y, 1)
            global xcorpus
            global ycorpus
            xcorpus.append(X)
            ycorpus.append(Y)
            first_line -= 1
#            print(X)

if __name__ == '__main__':
    init('./wiki-sample.word')

    for i in range(N):
        print('iter', i)
        sampleCorpus()
        if i % 1 == 0:
            with open('./wiki-nonpara.out{0:02d}'.format(int(i/1)), 'w') as f:
                for i in range(len(xcorpus)):
                    f.write(' '.join([ x + '/' + str(y) for x, y in zip(xcorpus[i][1:len(xcorpus[i])-1], ycorpus[i][1:len(ycorpus[i])-1])]))
                    f.write('\n')
        S += 1
