# a CallGraph is a CallGraphTree.
# a CallGraphTree is a tree of CallGraphNodes.
# a CallGraph

from graphviz import Digraph
from itertools import *

import random, copy




class CallGraph():
    def ___init__(self, root):
        self.root = root

class CallTree():
    def __init__(self, label, parent, optional=False, alternative=None):
        self.parent = parent
        self.label = label
        self.children = set()
        self.optional = optional
        if self.parent is None:
            self.alternative = None
        else:
            self.alternative = alternative

        if parent is not None:
            parent.add_child(self)

    def __str__(self):
        return self.label + "(" + ",".join(map(lambda x: x.label or "NONE", self.children)) + ") [" + str(self.parent) + "]"

    def min_failure_scenario_size(self):
        cardinality = 0
        for chld in self.children:
            if chld.optional == True:
                continue
            cardinality += 1
            tmp = self.alternative
            while tmp != None:
                cardinality += 1
                tmp = tmp.alternative
        return cardinality

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

    def inject_new(self, faultset):
        # new design: return the resulting call tree or None if it failed.
        # do NOT side-effect on faultset; instead, operate on a deep copy of it.

        # whoa is this a thing
        new_tree = copy.deepcopy(self)

        if new_tree.inject(faultset):
            return None
        else:
            return new_tree


    def inject(self, faultset):
        #print "inject " + str(faultset) + " at " + str(self)
        if self.label in faultset:
            return self.die(faultset)
        for chld in frozenset(self.children):
            if chld == self.alternative:
                continue
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
            while str(self.alternative.label) in faultset:
                tmp = self.alternative
                if tmp.alternative:
                    self.alternative = tmp.alternative
            if self.parent is not None:
                # The alternative is a child of the original instance
                # Since the original instance is failing, the alternative
                # now becomes child of the parent
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

    def print_graph(self):
        print self.label
        print "Children:"
        for child in self.children:
            print child.label
        for child in self.children:
            child.print_graph()

    '''
    This function renders the generated graph to dot
    Arguments
    alternates: set to True to display alternate paths in case of failure of service instance
    '''
    def to_dot(self, alternates=False):
        dot = Digraph("CallGraph", format = "pdf")

        # No alternates are displayed
        # active_nodeset retruns no alternate nodes,
        # edgeset() has alternates set to False by default
        if not alternates:
            for node in self.active_nodeset():
                if node.optional:
                    clr = "grey"
                else:
                    clr = "black"
                dot.node(node.label, color = clr)
            dot.edges(self.edgeset())
        else:
        # To logic here is to define subgraphs for all nodes and their alternatives to have the
        # same rank. Since the alternative has the original service node as parent, we use the
        # 'processed' variable to keep track of the nodes which have been processed so far
            num = 1
            children = [ self ]
            processed = []
            while len(children) > 0:
                node = children.pop(0)
                while node in processed and len(children)>0:
                    node = children.pop(0)

                if len(children)==0 and node in processed:
                    break

                sname = 'subgraph' + str(num)
                s = Digraph(sname)
                s.attr('graph', rank='same')

                while node is not None:
                    if node.optional:
                        clr = "grey"
                    else:
                        clr = "black"
                    s.node(node.label, color=clr)
                    processed.append(node.label)
                    children.extend(node.children)

                    node = node.alternative

                num += 1
                dot.subgraph(s)

            # A node's children as well as children of alternates are presented by solid arrows
            regular = self.edgeset(alternates)
            dot.edges(regular)
            # Alternates to nodes are repesented by dashed arrows
            dot.attr('edge', style='dashed')
            alt_edges = self.alt_edgeset()
            dot.edges(alt_edges)
        return dot

    def active_nodeset(self):
        ret = set([self])
        for chld in self.children:
            if chld != self.alternative:
                ret = ret.union(chld.active_nodeset())
        return ret

    def nodeset(self):
        ret = set([self])
        for chld in self.children:
            ret = ret.union(chld.nodeset())

        if self.alternative:
            ret.add(self.alternative)
            for chld in self.alternative.children:
                ret = ret.union(chld.nodeset())

        return ret

    def edgeset(self, alternates=False):
        if self.children == []:
            return set()
        else:
            sub = set()
            for chld in self.children:
                # If the child node is not an alternative, process it and its children
                if chld != self.alternative:
                    sub.add((self.label, chld.label))
                    sub = sub.union(chld.edgeset(alternates))
                # if the child node is an alternative, do not process its children if
                # we do not want to display alternate paths
                elif alternates:
                    sub = sub.union(chld.edgeset(alternates))
            # if the node being processed has an alternative, only process it if we want
            # to display alternate paths
            if self.alternative and alternates:
                for chld in self.alternative.children:
                    if chld != self.alternative.alternative:
                        sub.add((self.alternative.label, chld.label))
                    sub = sub.union(chld.edgeset(alternates))
            return sub

    # Return edges between a node and its altenrative
    def alt_edgeset(self):
        alt_edges = set()
        for chld in self.children:
            alt_edges = alt_edges.union(chld.alt_edgeset())
        if self.alternative:
            alt_edges.add((self.label, self.alternative.label))
            for chld in self.alternative.children:
                alt_edges = alt_edges.union(chld.alt_edgeset())
        return alt_edges

#class RandomCallTree():
#    def __init__(self, parent, depth, maxwidth):
