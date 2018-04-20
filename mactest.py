# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 18:48:48 2018

@author: rober
"""

import om as mac

s = mac.Shell()

s.interpret('(cond ~a True ~b) -> ([unw ~a])')
s.interpret('(cond ~a False ~b) -> ([unw ~b])')
#s.interpret('(~a for ~n) -> (cond (pop ~a | ~a for [~n - 1]) [bool ~n] ())') #KEEP
s.interpret('(~a while ~b) -> (cond (unw ~a | ~a while ~b) [bool [unw ~b]] () )')


s.interpret('n -> 10')
#s.interpret('m -> 1')
#s.interpret('o -> 2')

print('**********')

s.interpret('(pr n [(n) -> {n - 1}]) while (n > 0)')

#s.interpret('**********')
#s.interpret('10')

#s.interpret('(pr n [(o) -> {n + m}] [(n) -> {m}] [(m) -> {o}]) while (n < 100)') #fibonacci