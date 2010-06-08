#!/usr/bin/env python
#-*- coding:utf-8 -*-
  
import unittest
from aterm import decode, ATerm
 
class TestDecode(unittest.TestCase):
    def de(self,l,r):
        lval = decode(l)
        self.assertEquals()
    
    def test_simple(self):
        t = decode("T")
        self.assert_(isinstance(t, ATerm))
        self.assertEquals(t.name, "T")
        self.assertEquals(len(t), 0)
        
    def test_allatonce(self):
        t = decode('T("", "bla", "bla" , S([ "", "bla", "bla" ] ))')
        self.assert_(isinstance(t, ATerm))
        self.assertEquals(t.name, "T")
        self.assertEquals(len(t), 4)

class TestTree(unittest.TestCase):
    def test_tree(self):
        t = decode('A(B(C()),[])')
        self.assertEquals(t[0].name, "B")
        self.assertEquals(t[0].up, t)
        self.assertEquals(t[1].up, t)

class TestEncode(unittest.TestCase):
    def de(self,src,enc=None):
        d = decode(src)
        if enc is None:
            enc = src
        self.assertEquals(repr(d),enc)
        
    def test_tree(self):
        self.de('A()')
        self.de('A','A()')
        self.de('A("")')
        self.de('A("b")')
        self.de('A([])')
        self.de('A([B()])')
        self.de('A([B(),C()])')
        
class TestFind(unittest.TestCase):
    def test_tree(self):
        t = decode('A(B(C(D())),[])')
        r = [i for i in t.findall('C') ]
        self.assertEquals(len(r), 1)
        self.assertEquals(r[0][0].name,"D")
                       
if __name__ == '__main__':
    unittest.main()
 
