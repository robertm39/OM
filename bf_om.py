# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 17:55:22 2018

@author: rober
"""

def add_bf(shell):
#    shell.interpret('(PROG-I) -> 0')
#    shell.interpret('(prog) -> ()')
    
#    shell.interpret('(ENS-VAL) -> (cond () [[ptr] has val] (set [ptr] val 0.0))')
    shell.interpret('(WIPE-TAPE) -> ( (get tape ~a) -> (0.0))')
    shell.interpret('(ENS-VAL) -> (cond () [tape has [ptr]] (set tape [ptr] 0.0))')
    
    shell.interpret('(PTR-R) -> ([ptr -> [[ptr] + 1]] ENS-VAL)')
    shell.interpret('(PTR-L) -> ([ptr -> [[ptr] - 1]] ENS-VAL)')
    
    shell.interpret('(INC) -> (set tape [ptr] [[get tape [ptr]] + 1])')
    shell.interpret('(DEC) -> (set tape [ptr] [[get tape [ptr]] - 1])')
    
    shell.interpret('(CHR-O) -> (pr [char [get tape [ptr]]])')
    shell.interpret('(CHR-I) -> (set tape [ptr] [ord [ind 0 [expd [inp]]]])')
    
    shell.interpret('(L-LP) -> (cond (PROG-I -> [match-rb [PROG-I] [prog]]) [[get tape [ptr]] is 0.0] ())')
    shell.interpret('(R-LP) -> (cond (PROG-I -> [match-lb [PROG-I] [prog]]) [not [[get tape [ptr]] is 0.0]] ())')
    
    shell.interpret('(DO-BF ~a) -> ()') #Get rid of comments
    shell.interpret('(DO-BF > ) -> (PTR-R)')
    shell.interpret('(DO-BF < ) -> (PTR-L)')
    shell.interpret('(DO-BF + ) -> (INC)')
    shell.interpret('(DO-BF - ) -> (DEC)')
    shell.interpret('(DO-BF . ) -> (CHR-O)')
    shell.interpret('(DO-BF , ) -> (CHR-I)')
    shell.interpret('(DO-BF `[ ) -> (L-LP)')
    shell.interpret('(DO-BF `] ) -> (R-LP)')
    
    shell.interpret('(run-bf ~prog) -> (loc c ([ptr -> 0.0] [ENS-VAL] [WIPE-TAPE] [PROG-I -> 0] [prog -> (~prog)] [ ( [c -> {[ind [PROG-I] [prog]]} ] [DO-BF [c]] [PROG-I -> [[PROG-I] + 1]] ) while ([PROG-I] < [len [prog]]) ] ) )')
    shell.interpret('(rbf) -> (run-bf [expd [inp]])')