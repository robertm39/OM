# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:47:08 2018

@author: rober
"""

import om
import base_om_code as boc

s = om.Shell()
boc.add_all(s)

while True:
    line = input('LINE:')
#    print('interpreting: ' + line)
#    print('')
    s.interpret(line, do_print=True)
    
#(area ~a) -> ( cond ([get ~a width] * [get ~a height]) [[get ~a type] is Rect] (area ~a))