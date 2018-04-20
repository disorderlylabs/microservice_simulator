from pytest import *
from sim import *
from ldfi_py.pbool import *
import ldfi_py.pilp
import ldfi_py.psat


from cg_generator import CGGenerator
from naive_ldfi import NaiveLDFI

#MAGIC = 2341
MAGIC = 1234

import unittest

class MyTest(unittest.TestCase):

    def basic(self):
        ct = CallTree("A", None)
        cld = CallTree("B", ct, True)
        cld = CallTree("C", ct)
        cld2 = CallTree("D", cld, True)
    
        return ct

    def bigger(self):
        a = CallTree("A", None)
        b = CallTree("B", a, False, CallTree("B2", None))
        c = CallTree("C", a, True)
        d = CallTree("D", b)
        e = CallTree("E", b)
        f = CallTree("F", c)
        g = CallTree("G", c)
        return a

    def Ntest_graphs(self):
        bas = self.basic()
        self.assertEqual(bas.depth(), 0)
        self.assertEqual(bas.bottom(), 2)

    def Ntest_faults(self):
        baset = self.basic()
       
        print "INO "  + str(baset.inject("B")) 

        assert(not self.basic().inject("B"))
        assert(self.basic().inject("C"))
        assert(self.basic().inject("A"))
        assert(not self.basic().inject("D"))

        baset.inject(set("D"))
        baset.to_dot().render("foo")  


    def Ntest_bigger(self):
        baset = self.bigger()

        baset.to_dot().render("bar")


        assert(not self.bigger().inject("F"))
        assert(not self.bigger().inject("G"))
        assert(not self.bigger().inject("C"))
        assert(not self.bigger().inject("B"))
        assert(not self.bigger().inject("D"))
        assert(not self.bigger().inject("E"))

        assert(self.bigger().inject(["B", "B2"]))
        assert(self.bigger().inject(["D", "B2"]))
        assert(self.bigger().inject(["E", "B2"]))

        labels = set(map(lambda x: x.label, baset.nodeset()))
  
        print "labels is " + str(labels) 
        #self.assertEqual(labels, set(["A", "B", "C", "E", "D"])) 

        print "OK"
        baset.to_dot().render("baz")
        print "DONE"    

    def labels(self, t):
        return set(map(lambda x: x.label, t.nodeset()))
    
    def Ntest_b2(self):
        baset = self.bigger()
        assert(not baset.inject("F"))
        self.assertEqual(self.labels(baset), set(["A", "B", "E", "D", "B2"]))

        baset = self.bigger()
        assert(not baset.inject("E"))
        self.assertEqual(self.labels(baset), set(["A", "B2", "C", "F", "G"]))


        baset = self.bigger()
        assert(baset.inject(["E", "B2"]))

    def Ntest_fi(self):
        failures = 0
        baset = self.bigger()
        ft = FaultInjector(baset)
        self.assertEqual(len(list(ft.all_faults())), ft.all_faults_cnt())

        for fault in ft.all_faults():
            bt = self.bigger()
            ret = bt.inject(fault)
            if ret:
                print "failure " + str(fault)
                failures += 1
            
        print "faults " + str(ft.all_faults_cnt()) + ", failures " + str(failures)

    def Ntest_generate(self):
        cg = CGGenerator(5, MAGIC)
        g = cg.new_graph(4, 3)
        g.to_dot().render("NEWG")

        ft = FaultInjector(g)
        print "all: " + str(ft.all_faults_cnt())
        for fault in ft.all_faults():
            print "FAULT " + str(fault)

            if g.label in fault:
                continue
            cg = CGGenerator(5, MAGIC)
            g = cg.new_graph(4, 3)
            ret = g.inject(fault)
            #g.to_dot().render(str(fault))    
            if ret:
                print "failure " + str(fault)
                #failures += 1
                return fault

    def test_repeatbug(self):
        cg = CGGenerator(5, 19)
        g = cg.new_graph(4, 3)
        g.to_dot().render("before")
        ldfi = NaiveLDFI()
        ldfi.add_graph(g)
        print "FURF " + str(ldfi.current_formula())

        # [N1001, N390, N391]
        # [N232, N233, N418, N419]
        ret = g.inject(["N232", "N233", "N418", "N419"])
        g.to_dot().render("after")
        ldfi.add_graph(g)
        print "CURF " + str(ldfi.current_formula())

        print  "EDGES " + str(g.edgeset())

        print "G is  "  +str(g)
        print "ret is " + str(ret)
        

    def Ntest_ldfi(self):
        cg = CGGenerator(5, MAGIC)
        g = cg.new_graph(4, 3)
        ldfi = NaiveLDFI()
        ldfi.add_graph(g)
        sugg = ldfi.suggestions()
        soln = next(sugg)

        while soln:
            #print "SOLN " + str(soln)
            faultset = map(lambda x: str(x), soln)
            if g.label in faultset:
                print "WOOOO"
                soln = next(sugg)
                print "newSOLN " + str(soln)
                continue
                

            # need to implement a good deep copy for these things..
            cg = CGGenerator(5, MAGIC)
            g = cg.new_graph(4, 3)
            ret = g.inject(faultset)
            if ret:
                print "FAILURE!"
                return faultset

            ldfi.add_graph(g)
            #print "CURFORM: " + str(ldfi.current_formula())
            sugg = ldfi.suggestions()
            soln = next(sugg)


if __name__ == '__main__':
    unittest.main() 
