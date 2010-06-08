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
        self.assertEquals(len(t.params), 0)
        
    def test_allatonce(self):
           
        t = decode('T("", "bla", "bla" , S([ "", "bla", "bla" ] ))')
        self.assert_(isinstance(t, ATerm))
        self.assertEquals(t.name, "T")
        self.assertEquals(len(t.params), 4)

class TestTree(unittest.TestCase):
    def test_tree(self):
        t = decode('A(B(C()),[])')
        self.assertEquals(t.params[0].name, "B")
        self.assertEquals(t.params[0].up, t)
        self.assertEquals(t.params[1].up, t)

class TestEncode(unittest.TestCase):

    def de(self,src,enc=None):
        d = decode(src)
        if enc is None:
            enc = src
        self.assertEquals(repr(d),enc)
        
    def test_tree(self):
        self.de('A')
        self.de('A()','A')
        self.de('A("")')
        self.de('A([])')
        self.de('A([B])')
        self.de('A([B, C])')
                       
if __name__ == '__main__':
    unittest.main()
 
