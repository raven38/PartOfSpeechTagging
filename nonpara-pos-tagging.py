#!/usr/bin/env python
"""
This program is pos tagging by bayesian HMM
"""
import numpy as np
from numpy.random import rand, randint
from math import log
import argparse

c = dict({})
alpha = 0.001
N = 10000
S = 5
xcorpus = []
ycorpus = []

# P(s_{t+1} | s_t)
def Pcontext(j, i, beta, gamma):
    H = 1 / (S + 1)
    G = c.get(j, 0) / (c.get(None, 0) + gamma) + gamba / (c.get(None, 0) + gamma) * H
    p = c.get((i, j), 0) / (c.get(i, 0) + beta) + beta / (c.get(i, 0) + beta) * G
    return p

# P(y_t | s_t)
def Pword(j, i, beta, gamma):
    H = 1 / c.get(None, 0)
    G = c.get(j, 0) / (c.get(None, 0) + gamma) + gamma / (c.get(None, 0) + gamma) * H
    p = c.get((i, j), 0) / (c.get(i, 0) + beta) + beta / (c.get(i, 0) + beta) * G
    return p

#def P(a, b):
#    if a == S+1 or b == S+1:
#        return alpha / (c.get(b, 0) + alpha)
#    return (c.get((b,a), 0) + 1/S)/ (c.get(b,0) + alpha)                

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

def sampleTag(i, j, args):
    count((ycorpus[i][j-1], ycorpus[i][j]), -1)
    count((ycorpus[i][j], ycorpus[i][j+1]), -1)
    count((ycorpus[i][j], xcorpus[i][j]), -1)
    count(ycorpus[i][j], -1)
    count(xcorpus[i][j], -1)
    count(None, -1)
    beta = args.beta
    gammma = args.gamba
    beta_e = args.beta_emission
    gammma_e = args.gamma_emission

    p = {}
    for tag in range(1, S):
            p[tag] = Pcontext(tag, ycorpus[i][j-1],beta,gamma) * Pcontext(ycorpus[i][j+1], tag,beta,gamma) * Pword(xcorpus[i][j], tag,beta_e,gamma_e)
    p[S+1] = Pcontext(S+1, ycorpus[i][j-1],beta,gamma)  * Pcontext(ycorpus[i][j+1], S+1,beta,gamma) * Pword(xcorpus[i][j], S+1,beta_e,gamma_e)
    new_y = sampleOne(p)

    count((ycorpus[i][j-1], ycorpus[i][j]), 1)
    count((ycorpus[i][j], ycorpus[i][j+1]), 1)
    count((ycorpus[i][j], xcorpus[i][j]), 1)
    count(ycorpus[i][j], 1)
    count(xcorpus[i][j], 1)
    count(None, 1)    

    return new_y

def sampleCorpus(args):
    ll = 0
    max_S = 0
    for i in range(len(xcorpus)):
        next_y = [0]
        for j in range(1, len(xcorpus[i])-1):
            #            sampleTag(i, j)
            next_y.append(sampleTag(i, j, args))
            max_S = max(max_S, next_y[-1])
            ll += log(next_y[-1])
        next_y.append(0)
        for j in range(1, len(xcorpus[i])-1):
            count((ycorpus[i][j-1], ycorpus[i][j]), -1)
#            count((ycorpus[i][j], ycorpus[i][j+1]), -1)
            count((ycorpus[i][j], xcorpus[i][j]), -1)
            count(ycorpus[i][j], -1)
        ycorpus[i] = next_y
        for j in range(1, len(xcorpus[i])-1):
            count((ycorpus[i][j-1], ycorpus[i][j]), 1)
#            count((ycorpus[i][j], ycorpus[i][j+1]), 1)
            count((ycorpus[i][j], xcorpus[i][j]), 1)
            count(ycorpus[i][j], 1)
    global S
    S = max_S
    return ll

def init(infile):
    with open(infile, 'r') as f:
        first_line = 1
        for line in f:
            X = ['<s>'] + line[:-1].split(' ') + ['<s>']
            Y = [0] + list(randint(1, S+1, len(X)-2)) + [0]
            for i in range(1, len(X)-1):
                count((Y[i-1], Y[i]), 1)
#                count((Y[i], Y[i+1]), 1)
                count((Y[i], X[i]), 1)
            for x, y in zip(X, Y) :
                count(x, 1)
                count(y, 1)
                count(None, 1)
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
#            count((ycorpus[i][j], ycorpus[i][j+1]), -1)
            count((ycorpus[i][j], xcorpus[i][j]), -1)
        for y in ycorpus[i]:
            count(y, -1)

    cnt = 0
    for k, v in c.items():
        if v:            
            print(k, "can't delete", v)p
            cnt += 1
    print(cnt)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script is pos tagging of corpus')
    parser.add_argument('src', action='store', nargs=None, const=None, default=None, type=str, choices=None, help='File path where your file are located.')
    parser.add_argument('dst', action='store', nargs=None, const=None, default='./wiki-sample.out', type=str, choices=None)
    parser.add_argument('-n', action='store', type=int, default=100)
    parser.add_argument('-s', action='store', type=int, default=20)
    parser.add_argument('--beta', action='store', type=float, default=1)
    parser.add_argument('--gamma', action='store', type=float, default=1)
    parser.add_argument('--beta_emission', actino='store', type=float, default=1)
    parser.add_argument('--gamma_emission', action='store', type=float, default=1)
    args = parser.parse_args()
    init(args.src)

    for i in range(N):
        ll = sampleCorpus(args)
        print(i, ll)
        if i % 100 == 0:
            with open(args.dst + '{0:02d}'.format(int(i/100)), 'w') as f:
                for i in range(len(xcorpus)):
                    f.write(' '.join([ x + '/' + str(y) for x, y in zip(xcorpus[i][1:len(xcorpus[i])-1], ycorpus[i][1:len(ycorpus[i])-1])]))
                    f.write('\n')

    deleteSample()
