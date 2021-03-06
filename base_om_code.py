# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 18:11:50 2018

@author: rober
"""

def add_conds(shell):
    shell.interpret('(cond ~a True ~b) -> (unw ~a)')
    shell.interpret('(cond ~a False ~b) -> (unw ~b)')

def add_loops(shell):
    shell.interpret('(~a while ~b) -> (cond ([unw ~a] ~a while ~b) unw ([bool [unw ~b]]) () )')
    shell.interpret('(~a ~n times) -> ( cond ([unw ~a ] ~a [[~n] - 1] times) [bool [[~n] > 0]] () )')
    
    shell.interpret('(~a FOR ~o IN ~l WITH ~i) -> ([~i -> 0] [ ( [[~o -> [ind [~i] ~l]] [unw ~a]] [~i -> [[~i] + 1]]) while ([~i] < [len [~l]])] )')
    shell.interpret('(~a for ~o in ~l) -> (~a FOR ~o IN ~l WITH [loc (i) (i)])')

def add_vars(shell):
    shell.interpret('(get ~obj ~var) -> ()')
    shell.interpret('(~obj has ~var) -> (False)')
    
    shell.interpret('(set ~obj ~var ~val) -> ( (get ~obj ~var) -> (~val) (~obj has ~var) -> (True) )')
    shell.interpret('(del ~obj ~var) -> ( (get ~obj ~var) -> () (~obj has ~var) -> (False) )')
    
def add_is(shell):
    shell.interpret('(~a is ~b) -> (False)')
    shell.interpret('(~a is ~a) -> (True)')#Depends on precendence

def add_bool(shell):
    shell.interpret('(not True) -> (False)')
    shell.interpret('(not False) -> (True)')
    
    shell.interpret('(False and ~b) -> (False)')
    shell.interpret('(True and ~b) -> (~b)')
    
    shell.interpret('(False or ~a) -> (~a)')
    shell.interpret('(True or ~a) -> (True)')
    
    shell.interpret('(False xor False) -> (False)')
    shell.interpret('(False xor True) -> (True)')
    shell.interpret('(True xor False) -> (True)')
    shell.interpret('(True xor True) -> (False)')

def add_lists(shell):
#    shell.interpret('(wcond ~a True ~b) -> (ind 0 ~a)')
#    shell.interpret('(wcond ~a False ~b) -> (ind 0 ~b)')
#    shell.interpret('(~a wwhile ~b) -> (wcond ([[ind 0 ~a] ~a wwhile ~b]) ind 0 ([bool [ind 0 ~b]]) ([]) )')
#    shell.interpret('(~a WFOR ~o IN ~l WITH ~i) -> ([~i -> 0] [ ( [[[~o -> [ind [~i] ~l]] [~a]] [~i -> [[~i] + 1]]]) wwhile ([[~i] < [len [~l]]])] )')
#    shell.interpret('(~a wfor ~o in ~l) -> (~a WFOR ~o IN ~l WITH [loc (i) (i)])')
#    shell.interpret('(unw ~l) -> ([loc (a) (a wfor a)] in ~l)')
    
    shell.interpret('(islist ~l) -> ([[expd ~l] is ()])')
    shell.interpret('(slice ~i1 ~i2 ~l) -> (loc (i) ([i -> [~i1]] [([ind [i] ~l] [i -> [[i] + 1]]) while ([[i] < ~i2])]))')
    shell.interpret('(ind ~i ~l) -> (ind [[len ~l] + [~i]] ~l) if ([~i] < 0)')
    shell.interpret('(~l1 conc ~l2) -> ({[unw ~l1] [unw ~l2]})')
    
    shell.interpret('(~l backward) -> (loc (i) ([i -> [[len ~l] - 1]] [ ([ind [i] ~l] [i -> [[i] - 1]]) while ([i] >= 0) ] ))')

def add_string_parse(shell):
    shell.interpret('LB -> `[ ')
    shell.interpret('RB -> `] ')
    
    shell.interpret('(match-rb ~ind ~l) -> (ind -1 {loc (num) (loc (i) (loc (char) ([num -> 1] [i -> [~ind]] [ ([i -> [[i] + 1]] [char -> [ind [i] ~l]] [cond (num -> [[num] + 1]) [[char] is [LB] ] () ] [cond (num -> [[num] - 1]) [[char] is [RB] ] ()]) while ([num != 0]) ] [i] ) ) ) } )')
    shell.interpret('(match-lb ~ind ~l) -> (ind -1 {loc (num) (loc (i) (loc (char) ([num -> -1] [i -> [~ind]] [ ([i -> [[i] - 1]] [char -> [ind [i] ~l]] [cond (num -> [[num] + 1]) [[char] is [LB] ] () ] [cond (num -> [[num] - 1]) [[char] is [RB] ] ()]) while ([num != 0]) ] [i] ) ) ) } )')
    shell.interpret('(match-b ~ind ~l) -> (cond (match-rb ~ind ~l) [[ind ~ind ~l] is [LB]] (match-lb ~ind ~l))')

def add_all(shell):
    add_conds(shell)
    add_loops(shell)
    add_vars(shell)
    add_is(shell)
    add_bool(shell)
    add_lists(shell)
    add_string_parse(shell)
