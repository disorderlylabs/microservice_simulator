#!/usr/bin/python

from cg_generator import CGGenerator
from naive_ldfi import NaiveLDFI
from injectors import FaultInjector, RandomFaultInjector, HeuristicFaultInjector

import random
import json
import sys

# LOLOLOLOLOL
sys.setrecursionlimit(1000000)

MAXWIDTH = 5
MAXDEPTH = 4
MAXALTS = 3

RANDOM_TARGET = 2

maxiterations = 10000


class Result():
    def __init__(self, solution=None, iterations=None):
        self.solution = solution
        self.iterations = iterations

    def __str__(self):
        #print "IN STR"
        return str(self.solution) + " in " + str(self.iterations) + " attempts"

def do_ldfi(g):
    ldfi = NaiveLDFI()
    ldfi.add_graph(g)
    sugg = ldfi.suggestions()
    try:
        soln = next(sugg)
    except StopIteration:
        return Result(None, iterations)

    iterations = 0
    while soln:
        #print iterations
        iterations += 1
        #print "SOLN " + str(soln)
        faultset = map(lambda x: str(x), soln)

        if g.label in faultset:
            if iterations > maxiterations:
                return Result(None, iterations)

            #print "WOOOO"
            try:
                soln = next(sugg)
            except StopIteration:
                return(None, iterations)
            print "newSOLN " + str(soln)
            continue

        ret = g.inject_new(faultset)
        if ret is None:
            return Result(faultset, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)

            # if we are down to just suggesting" FAIL NODE 1!  then we are done"
            if ret.children == set():
                return Result(None, iterations)
            else:
                ldfi.add_graph(ret)
                #print "CURFORM: " + str(ldfi.current_formula())
                sugg = ldfi.suggestions()
                try:
                    soln = next(sugg)
                except StopIteration:
                    return(None, iterations)

def do_bruteforce(g):
    ft = FaultInjector(g)
    iterations = 0
    #print "all: " + str(ft.all_faults_cnt())
    for fault in ft.all_faults():
        iterations += 1
        #print iterations
        if g.label in fault:
            if iterations > maxiterations:
                return Result(None, iterations)
            continue
        ret = g.inject_new(fault)
        if ret is None:
            return Result(fault, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)
    return Result(None, iterations)


def do_random(g):
    ft = RandomFaultInjector(g)
    iterations = 0
    while True:
        iterations += 1
        #print iterations
        fault = ft.next_fault(RANDOM_TARGET)
        if g.label in fault:
            if iterations > maxiterations:
                return Result(None, iterations)
            continue

        ret = g.inject_new(fault)
        if ret is None:
            return Result(fault, iterations)
        else:
            if iterations > maxiterations:
                return Result(None, iterations)

def do_heuristic(g):
    ft = HeuristicFaultInjector(g)
    iterations = 0
    while True:
        iterations += 1
        #print iterations
        sugg = ft.next_fault()
        try:
            prev_faults = ft.get_faults_injected()
            fault = next(sugg)
            while fault in prev_faults:
                fault = next(sugg)
        except StopIteration:
            return Result(None, iterations)

        ft.add_faults_injected(fault)
        ret = g.inject_new(fault)
        if ret is None:
            return Result(fault, iterations)
        else:
            if iterations > maxiterations:
                return Resut(None, iterations)
            ft.update_heuristic(ret)

op_file = sys.argv[1]
print "Nodes, edges, ldfi, random, bruteforce"

res_categories = {}
for j in range(50):
    #i = j + 64
    i =  j
    cg = CGGenerator(MAXWIDTH, i)
    g = cg.new_graph(MAXDEPTH, MAXALTS)
    g.to_dot().render(str(i))
    print "GRAPH " + str(i) + ":" + str(len(g.nodeset())) + " nodes, " + str(len(g.edgeset())) + " edges"
    print "depth " + str(g.depth())
    print "bottom " + str(g.bottom())
    if g.bottom() == 0:
        continue

    print "Finding LDFI solution"
    l = do_ldfi(g)
    print "Finding random solution"
    r = do_random(g)
    print "Finding bruteforce solution"
    b = do_bruteforce(g)
    print "Finding heuristic solution"
    h = do_heuristic(g)

    print "|".join(map(lambda x: str(x), [j, len(g.nodeset()), len(g.edgeset(alternates=True)), l.solution, l.iterations, r.solution, r.iterations, b.solution, b.iterations, h.solution, h.iterations]))

    soln_len = g.min_failure_scenario_size()
    if soln_len not in res_categories:
        res_categories[soln_len] = []

    tmp = {}
    tmp['l_iter'] = l.iterations
    tmp['b_iter'] = b.iterations
    tmp['r_iter'] = r.iterations
    tmp['h_iter'] = h.iterations
    tmp['alternates'] = MAXALTS
    tmp['nodes'] = len(g.nodeset())
    tmp['edges'] = len(g.edgeset(alternates=True))
    res_categories[soln_len].append(tmp)

f = open(op_file, "w")
json.dump(res_categories, f, indent=0)
f.close()
