# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:47:08 2018

@author: rober
"""

import om
import base_om_code as boc
import bf_om

s = om.Shell()
boc.add_all(s)
bf_om.add_bf(s)

while True:
    line = input('LINE:')
    s.interpret(line, verbose=False, do_print=True)