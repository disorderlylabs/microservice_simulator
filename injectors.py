# I totally lied about these classes having a common ancestor.
# but perhaps it could be that way...

from itertools import *
import random
import re

class RandomFaultInjector:
    def  __init__(self, graph):
        self.graph = graph

    def next_fault(self, target):
        faults = []
        prob = (float(target) / float(len(self.graph.active_nodeset())))
        #print "PROB " + str(prob)
        for n in self.graph.active_nodeset():
            # oh man I suck at this
            roll = random.uniform(0, 1)
            #print "roll is " + str(roll)
            if roll <= prob:
                #print "YAY"
                faults.append(n.label)
            #else:
                #print "sorry, " + str(roll) + " > " + str(prob)
        return faults

def natural_sort_key(s):
    _nsre = re.compile('([0-9]+)')
    return [int(text) if text.isdigit() else text.lower()
        for text in re.split(_nsre, s)]

class FaultInjector:
    def __init__(self, graph):
        self.graph = graph

    def all_faults(self):
        n = map(lambda x: x.label, self.graph.active_nodeset())
        n.sort(key=natural_sort_key)
        return chain.from_iterable(combinations(n, r) for r in range(1, len(n)+1))

    def all_faults_cnt(self):
        print len(self.graph.active_nodeset())
        return (2 ** len(self.graph.active_nodeset())-1)


class DemonicFaultInjector:
    def __init__(self, graph):
        self.graph = graph

    def all_faults(self):
        return inject(self.graph)

    #def inject(self, node):
    #    if node.optional:
    #
    #    else:


#class NaiveFaultInjector(FaultInjector):

