# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 18:47:08 2018

@author: rober
"""

import om

s = om.Shell()

while True:
    line = input('LINE:')
#    print('interpreting: ' + line)
#    print('')
    s.interpret(line)