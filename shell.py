# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:47:08 2018

@author: rober
"""

import om
import base_om_code as boc

s = om.Shell()
boc.add_conds(s)
boc.add_loops(s)
boc.add_vars(s)

while True:
    line = input('LINE:')
#    print('interpreting: ' + line)
#    print('')
    s.interpret(line)