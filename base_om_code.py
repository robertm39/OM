# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 18:11:50 2018

@author: rober
"""

def add_conds(shell):
    shell.interpret('(cond ~a True ~b) -> ([unw ~a])')
    shell.interpret('(cond ~a False ~b) -> ([unw ~b])')

def add_loops(shell):
    shell.interpret('(~a while ~b) -> (cond ([unw ~a] | ~a while ~b) unw ([bool [unw ~b]]) () )')
#    shell.interpret('(~a for ~o in ~l) -> (loc i ([i -> 0] [ ( [[~o -> [ind [i] ~l]] [unw ~a]] [i -> [[i] + 1]]) while ([i] < [len [~l]])] ))')
    shell.interpret('(~a ~n times) -> ( cond ([unw ~a ] | ~a [[~n] - 1] times) [bool [[~n] > 0]] () )')
    
    shell.interpret('(~a FOR ~o IN ~l WITH ~i) -> ([~i -> 0] [ ( [[~o -> [ind [~i] ~l]] [unw ~a]] [~i -> [[~i] + 1]]) while ([~i] < [len [~l]])] )')
    shell.interpret('(~a for ~o in ~l) -> (~a FOR ~o IN ~l WITH [loc i (i)])') #This works, but for some time it didn't, and I have no idea why.


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
    shell.interpret('(False and False) -> (False)')
    shell.interpret('(False and True) -> (False)')
    shell.interpret('(True and False) -> (False)')
    shell.interpret('(True and True) -> (True)')
    shell.interpret('(False or False) -> (False)')
    shell.interpret('(False or True) -> (True)')
    shell.interpret('(True or False) -> (True)')
    shell.interpret('(True or True) -> (True)')
    shell.interpret('(False xor False) -> (False)')
    shell.interpret('(False xor True) -> (True)')
    shell.interpret('(True xor False) -> (True)')
    shell.interpret('(True xor True) -> (False)')

def add_lists(shell):
    shell.interpret('(islist ~l) -> ([[expd ~l] is ()])')
    shell.interpret('(slice ~i1 ~i2 ~l) -> (loc i ([i -> [~i1]] [([ind [i] ~l] [i -> [[i] + 1]]) while ([[i] < ~i2])]))')
    shell.interpret('(ind ~i ~l) -> (ind [[len ~l] + [~i]] ~l) if ([~i] < 0)')
    shell.interpret('(~l1 conc ~l2) -> ({[unw ~l1] [unw ~l2]})')

def add_all(shell):
    add_conds(shell)
    add_loops(shell)
    add_vars(shell)
    add_is(shell)
    add_bool(shell)
    add_lists(shell)
