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
s.interpret('(cond (~a) 0 (~b)) -> (~a)')
s.interpret('(cond (~a) 1 (~b)) -> (~b)')
#print('')
#print('Testing:')
#print('')
s.interpret('cond (False) 0 (True)')
#print('')
#s.interpret('a')