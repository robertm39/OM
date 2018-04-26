# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 18:48:48 2018

@author: rober
"""

import om
import base_om_code as boc

s = om.Shell()

boc.add_conds(s)
boc.add_loops(s)
boc.add_vars(s)

s.interpret('n -> 10')

print('**********')

#s.interpret('([pr [[n] ** 2]] [(n) -> {[n] - 1}]) while ([n] >= 0)')
s.interpret('(a) 5 times')

#s.interpret('**********')
#s.interpret('10')

#s.interpret('(pr n [(o) -> {n + m}] [(n) -> {m}] [(m) -> {o}]) while (n < 100)') #fibonacci