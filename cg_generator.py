import random
from sim import *

class CGGenerator():
    # trying to channel both Ash*

    def __init__(self, maxwidth, seed = None):
        random.seed(seed)
        self.maxwidth = maxwidth
        self.cnt = 0


    def skolem(self):
        self.cnt += 1
        return "N" + str(self.cnt)


    def callgraph(self, parent, maxdepth, maxalternatives, mandatory = False):
        nchildren = random.randint(1, self.maxwidth)
        if mandatory:
            optional = False
        else:
            optional = (random.randint(0,1) == 0)

        name = self.skolem()
        #print "CREATE NODE " + str(name) + " optional " + str(optional)

        alt = None
        a = CallTree(name, parent, optional, alt)
        #print "I just created " + str(a) + " parent " + str(a.parent)

        if parent is not None and not optional and random.randint(0, maxalternatives) > 0:
            #print "I have an alter ego."
            # I shall have an alter ego
            alt = self.callgraph( a, maxdepth, maxalternatives-1, True)
            #print "NODE " + name + "has alternative " + str(alt)
            a.add_alternative(alt)

        # now decide if we have children, and if so how many.
        #print "flip a coin from 0 - " + str(maxdepth) + " to decide if " + str(a) + "spawns"
        if random.randint(0, maxdepth) > 0:
            #print "NODE " + name + " shall have " + str(nchildren)+ " children"
            # I shall reproduce

            #for i in range(nchildren):
                #print "lalala " + str(i)

            for i in range(nchildren):
                #print "OK OK " + str(a) + " at " + str(i)
                chld = self.callgraph(a, maxdepth-1, maxalternatives)
                #print "NODE " + name + " has child " + str(chld)
                # something funny is going to happen with the children of alternatives
                a.add_child(chld)
        #else:
        #    print "NODE " + name + " is childless"


        return a

    def new_graph(self, maxdepth, maxalternatives):
        # this is hard to get right, bear with me
        # first, decide if I am a leaf. pick a number between 0 and maxdepth; if it's zero, I am a leaf.

        return self.callgraph(None, maxdepth, maxalternatives, True)

