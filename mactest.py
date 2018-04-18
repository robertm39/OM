# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 18:48:48 2018

@author: rober
"""

import om as mac

s = mac.Shell()
#tok = '(hello world) normal tokens <cool brackets> /cooler brackets\\ ( [{} ])'
tok = '(a b) -> (b a)'
#print(s.tokenize(tok))
s.interpet(tok)
print('')
s.interpet('/b\ -> {c}')
print('')
s.interpet('a')