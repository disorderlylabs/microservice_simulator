from cg_generator import CGGenerator
from naive_ldfi import NaiveLDFI
from injectors import FaultInjector, RandomFaultInjector

import random

import sys


# LOLOLOLOLOL
sys.setrecursionlimit(1000000)

MAXWIDTH = 5
MAXDEPTH = 4
MAXALTS = 3

maxiterations = 5000


class Result():
    def __init__(self, solution, iterations):
        self.solution = solution
        self.iterations = iterations

    def __str__(self):
        #print "IN STR"
        return str(self.solution) + " in " + str(self.iterations) + " attempts"


def do_ldfi(magic):
    cg = CGGenerator(MAXWIDTH, magic)
    g = cg.new_graph(MAXDEPTH, MAXALTS)
    ldfi = NaiveLDFI()
    ldfi.add_graph(g)
    sugg = ldfi.suggestions()
    soln = next(sugg)

    iterations = 0
    while soln:
        iterations += 1
        #print "SOLN " + str(soln)
        faultset = map(lambda x: str(x), soln)
        if g.label in faultset:
            print "WOOOO"
            soln = next(sugg)
            print "newSOLN " + str(soln)
            continue

        # need to implement a good deep copy for these things..
        cg = CGGenerator(MAXWIDTH, magic)
        g = cg.new_graph(MAXDEPTH, MAXALTS)
        ret = g.inject(faultset)
        if ret:
            #print "FAILURE!"
            return Result(faultset, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)

            #print "We are gonna add this graph " + str(g)
            #print "with edges " + str(g.edges())
            # if we are down to just suggesting" FAIL NODE 1!  then we are done"
            if g.children == set():
                return Result(None, iterations)
            else:
                ldfi.add_graph(g)
                #print "CURFORM: " + str(ldfi.current_formula())
                sugg = ldfi.suggestions()
                soln = next(sugg)

def do_bruteforce(magic):
    cg = CGGenerator(MAXWIDTH, magic)
    g = cg.new_graph(MAXDEPTH, MAXALTS)
    g.to_dot().render("NEWG")

    ft = FaultInjector(g)
    iterations = 0
    print "all: " + str(ft.all_faults_cnt())
    for fault in ft.all_faults():
        #print "FAULT " + str(fault)
        iterations += 1
        if g.label in fault:
            continue
        cg = CGGenerator(MAXWIDTH, magic)
        g = cg.new_graph(MAXDEPTH, MAXALTS)
        ret = g.inject(fault)
        #g.to_dot().render(str(fault))
        if ret:
            #print "failure " + str(fault)
            #failures += 1
            return Result(fault, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)


def do_random(magic):
    cg = CGGenerator(MAXWIDTH, magic)
    g = cg.new_graph(MAXDEPTH, MAXALTS)
    g.to_dot().render("NEWG")

    ft = RandomFaultInjector(g)
    iterations = 0
    while True:
        iterations += 1
        fault = ft.next_fault(2)
        if g.label in fault:
            continue

        if len(fault) > 1:
            print "FALT is " + str(fault)

        cg = CGGenerator(MAXWIDTH, magic)
        g = cg.new_graph(MAXDEPTH, MAXALTS)
        ret = g.inject(fault)
        #print "Fault " + str(fault)
        if ret:
            print "failure " + str(fault)
            #failures += 1
            return Result(fault, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)
        
        




for j in range(100):
    i = j + 64
    cg = CGGenerator(MAXWIDTH, i)
    g = cg.new_graph(MAXDEPTH, MAXALTS)
    g.to_dot().render(str(i))
    print "GRAPH " + str(i) + ":" + str(len(g.nodeset())) + " nodes, " + str(len(g.edgeset())) + " edges"
    #print "depth " + str(g.depth())
    #print "bottom " + str(g.bottom())
    if g.bottom() == 0:
        continue

    l = do_ldfi(i)
    r = do_random(i)
    b = do_bruteforce(i)

    print "LDFI: " + str(l)
    print "BRUTE: " + str(b)
    #print "Random: " + str(r)
