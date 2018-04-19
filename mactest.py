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
s.interpret('(cond (~a) True (~b)) -> (~a)')
s.interpret('(cond (~a) False (~b)) -> (~b)')
#print('')
#print('Testing:')
#print('')
#s.interpret('cond (One) True (Two)')
#s.interpret('cond (One) False (Two)')
s.interpret('(for ~a ~n) -> (cond ((~a for ~a [~n - 1])) [bool ~n] (nop))')
s.interpret('for 1 3')
#print('')
#s.interpret('a')