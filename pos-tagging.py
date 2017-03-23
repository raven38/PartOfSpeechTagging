#!/usr/bin/env python
"""
This program is pos tagging by bayesian HMM
"""
import numpy as np
from numpy.random import rand, randint
from math import log

c = dict({})
alpha = 0.001
N = 10000
S = 21
xcorpus = []
ycorpus = []

def P(a, b):
    return (c.get((b,a), 0) + alpha/S) / (c.get(b,0) + alpha)                

def count(key, value):
    if key in c:
        c[key] += value
    else:
        c[key] = value

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
    for tag in range(1, S):
        if (ycorpus[i][j-1], tag) in c and (tag, ycorpus[i][j+1]) in c and (tag, xcorpus[i][j]) in c and tag in c and ycorpus[i][j-1] in c:
            p[tag] = P(tag, ycorpus[i][j-1]) * P(ycorpus[i][j+1], tag) * P(xcorpus[i][j], tag)

    new_y = sampleOne(p)

    count((ycorpus[i][j-1], ycorpus[i][j]), 1)
    count((ycorpus[i][j], ycorpus[i][j+1]), 1)
    count((ycorpus[i][j], xcorpus[i][j]), 1)

    return new_y

def sampleCorpus():
    ll = 0
    for i in range(len(xcorpus)):
        next_y = [0]
        for j in range(1, len(xcorpus[i])-1):
            #            sampleTag(i, j)
            next_y.append(sampleTag(i, j))
            ll += log(next_y[-1])
        next_y.append(0)
        for j in range(1, len(xcorpus[i])-1):
            count((ycorpus[i][j-1], ycorpus[i][j]), -1)
            count((ycorpus[i][j], ycorpus[i][j+1]), -1)
            count((ycorpus[i][j], xcorpus[i][j]), -1)
            count(ycorpus[i][j], -1)
        ycorpus[i] = next_y
        for j in range(1, len(xcorpus[i])-1):
            count((ycorpus[i][j-1], ycorpus[i][j]), 1)
            count((ycorpus[i][j], ycorpus[i][j+1]), 1)
            count((ycorpus[i][j], xcorpus[i][j]), 1)
            count(ycorpus[i][j], 1)
    return ll

def init(infile):
    with open(infile, 'r') as f:
        first_line = 1
        for line in f:
            X = ['<s>'] + line[:-1].split(' ') + ['<s>']
            Y = [0] + list(randint(1, S, len(X)-2)) + [0]
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

def deleteSample():
    for i in range(len(xcorpus)):
        for j in range(1, len(xcorpus[i])-1):
            count((ycorpus[i][j-1], ycorpus[i][j]), -1)
            count((ycorpus[i][j], ycorpus[i][j+1]), -1)
            count((ycorpus[i][j], xcorpus[i][j]), -1)
        for y in ycorpus[i]:
            count(y, -1)

    cnt = 0
    for k, v in c.items():
        if v:            
            print(k, "can't delte", v)
            cnt += 1
    print(cnt)

if __name__ == '__main__':
    init('./wiki-sample.word')
#    init('./simple.word')

    for i in range(N):
#        print('iter', i)
        ll = sampleCorpus()
        print(i, ll)
        if i % 100 == 0:
            with open('./wiki-sample.out{0:02d}'.format(int(i/100)), 'w') as f:
                for i in range(len(xcorpus)):
                    f.write(' '.join([ x + '/' + str(y) for x, y in zip(xcorpus[i][1:len(xcorpus[i])-1], ycorpus[i][1:len(ycorpus[i])-1])]))
                    f.write('\n')

    deleteSample()
