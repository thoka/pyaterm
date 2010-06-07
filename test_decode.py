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
       
                
if __name__ == '__main__':
    unittest.main()
 
