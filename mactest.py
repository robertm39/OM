# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 18:48:48 2018

@author: rober
"""

import om as mac

s = mac.Shell()
#tok = '(hello world) normal tokens <cool brackets> /cooler brackets\\ ( [{} ])'
#tok = '(a b) -> (b a)'
#print(s.tokenize(tok))
s.interpret('(cond ~a True ~b) -> ([pop ~a])')
s.interpret('(cond ~a False ~b) -> ([pop ~b])')

#s.interpret('(~a for ~n) -> (cond (pop ~a | ~a for [~n - 1]) [bool ~n] ())')
#s.interpret('(1) for 5')

s.interpret('(~a while ~b) -> (cond (pop ~a | ~a while ~b) [bool ~b] () )')
s.interpret('n -> 5')
s.interpret('(iter [n -> [n - 1]]) while n')