# a CallGraph is a CallGraphTree.
# a CallGraphTree is a tree of CallGraphNodes.
# a CallGraph

from graphviz import Digraph
from itertools import *

import random

    


class CallGraph():
    def ___init__(self, root):
        self.root = root

class CallTree():
    def __init__(self, label, parent, optional=False, alternative=None):
        self.parent = parent
        self.label = label
        self.children = set()
        self.optional = optional
        #self.alternative = alternative
        #self.add_alternative(alternative)
        if self.parent is None:
            #print "no root alternatives, please"
            self.alternative = None
        else:
            self.alternative = alternative
    
        if parent is not None:
            parent.add_child(self)

    def __str__(self):
        return self.label + "(" + ",".join(map(lambda x: x.label or "NONE", self.children)) + ") [" + str(self.parent) + "]"

    def add_parent(self, parent):
        self.parent = parent

    def set_mandatory(self):
        self.optional = False

    def add_child(self, chld):
        # PAA?
        chld.parent = self
        self.children.add(chld)

    def delete_child(self, chld):
        if chld in self.children:
            self.children.remove(chld)

    def add_alternative(self, alternative):
        if self.parent is None:
            print "no root alternatives, please"
        else:
            self.alternative = alternative
        

    def inject(self, faultset):
        #print "inject " + str(faultset) + " at " + str(self)
        if self.label in faultset:
            return self.die(faultset)
        for chld in frozenset(self.children):
            if chld.inject(faultset):
                return self.die(faultset)
        return False

    def die(self, faultset):
        #print str(self) + " is dying! tell mom " + str(self.parent)
        #print "par had " + str(len(self.parent.children))
        if self.parent is not None:
            self.parent.delete_child(self)

        #if self.alternative:
        #    print "ALT " + str(self.alternative)
        if self.alternative and not self.alternative.inject(faultset):
            #print str(self) + " SURVIVED"
            if self.parent is not None:
                self.parent.add_child(self.alternative)
            return False
        else:
            #print "OH BOYa " + str(not self.optional)
            return not self.optional
        


    def bottom(self):
        if self.children == set():
            return self.depth()
        else:
            return max(map(lambda x: x.bottom(), self.children))

    def depth(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.depth() + 1

    def to_dot(self):
        dot = Digraph("CallGraph", format = "pdf")
        for node in self.nodeset():
            if node.optional:
                #print "it's optiona"
                #shap = "oval"
                clr = "grey"
            else:
                #shap = "doublecircle"
                clr = "black"
            #dot.node(node.label, shape=shap)
            dot.node(node.label, color = clr)
        dot.edges(self.edgeset())
        return dot

    def active_nodeset(self):
        ret = set([self])
        for chld in self.children:
            ret = ret.union(chld.active_nodeset())
        return ret

    def nodeset(self):
        ret = set([self])
        for chld in self.children:
            ret = ret.union(chld.nodeset())

        if self.alternative:
            ret.add(self.alternative)
    
        return ret
        
        
    def edgeset(self):
        if self.children == []:
            return set()
        else:
            sub = set()
            for chld in self.children:
                if chld.edgeset() is not None:
                    sub = sub.union(chld.edgeset())
                sub.add((self.label, chld.label))
            return sub

#class RandomCallTree():
#    def __init__(self, parent, depth, maxwidth):
