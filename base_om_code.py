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
    shell.interpret('(~a for ~o in ~l) -> (loc i ([i -> 0] [ ( [[~o -> [ind [i] ~l]] [unw ~a]] [i -> [[i] + 1]]) while ([i] < [len [~l]])] ))')
    shell.interpret('(~a ~n times) -> ( cond ([unw ~a ] | ~a [[~n] - 1] times) [bool [[~n] > 0]] () )')

def add_vars(shell):
    shell.interpret('(get ~obj ~var) -> ()')
    shell.interpret('(~obj has ~var) -> (False)')
    
    shell.interpret('(set ~obj ~var ~val) -> ( (get ~obj ~var) -> (~val) (~obj has ~var) -> (True) )')
    shell.interpret('(del ~obj ~var) -> ( (get ~obj ~var) -> () (~obj has ~var) -> (False) )')