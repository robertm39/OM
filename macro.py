# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:16:39 2018

@author: rober
"""
#from numba import jitclass#, uint16, boolean

import om
import node as nd
from utils import normal
from utils import fill_in_form

def handle_cond_macro(form, product_form, cond_form, mappings, shell):
    cond_form = fill_in_form(cond_form, mappings)
    cond, changed = shell.apply_macros(cond_form)
    
    if cond == [normal('True')]:
        return fill_in_form(product_form, mappings)
    else:
        return fill_in_form(form, mappings)

#spec = [('form', Node),
#        ('ln', uint16[:]),
#        ('is_cond', boolean)]

#@jitclass#(spec)

#def is_free(form):
#    capture_names = []
#    for node in form:
#        if node.NodeType in nd.BRACKET_TYPES:
#            return False
#        if node.NodeType is nd.NodeType.CAPTURE:
#            if node.name in capture_names:
#                return False
#            capture_names.append(node.name)
#    return True

class Macro:
    def __init__(self,
                 form,
                 get_product=None,
                 product_form=None,
                 cond_form=None,
                 shell=None,
                 name='unknown macro'):
        self.form = form
        self.ln = len(form)
        self.name=name
        self.is_cond = cond_form != None
        
        if get_product != None:
            self.get_product = get_product
        elif product_form != None:
            if cond_form != None:
                self.get_product = lambda mappings: handle_cond_macro(form,
                                                                      product_form,
                                                                      cond_form,
                                                                      mappings,
                                                                      shell)
            else:
                self.get_product = lambda mappings: fill_in_form(product_form, mappings)
        else:
            raise AssertionError('No get_product or product_form')
    
    def __str__(self):
        return self.name
    
    def __lt__(self, other): #Less than -> runs earlier
        if self.ln > other.ln:
            return True
        if self.ln < other.ln:
            return False
        #self.ln == other.ln
        if self.time_added > other.time_added:
            return True
        return False
    
    #Whether this macro matches the given expression, starting at the left
    def matches(self, expr, norm_done=False, form=None, mappings=None, exact=False):
        form = self.form if form == None else form
        mappings = {} if mappings == None else mappings #Captured values: name -> node
        i = 0
        
        not_matches = False, {}, 0
        
        if len(expr) < len(form):
            return not_matches
        
        #For an exact match, the expr and the form must be the same length
        if exact and len(expr) > len(form):
            return not_matches
        
        for node in expr:
#        for i in (range(0, len(expr))  if not norm_done else self.check_indices):
#            node = expr[i]
            
            if node.val == '|': #blocks macro comprehension
                return not_matches
            
            f_node = form[i]
            
            if f_node.node_type is om.NodeType.CAPTURE: #Capture nodes
                name = f_node.val
                if name in mappings: #See whether the node matches the captured node
                    captured_node = mappings[name]
                    if node != captured_node:
                        return not_matches
                else: #Capture this node
                    mappings[name] = node
#            elif f_node.node_type is om.NodeType.PAREN: #A list
            elif f_node.node_type in om.BRACKET_TYPES: #A list
                if f_node.node_type != node.node_type:
                    return not_matches
                does_match, mappings, length = self.matches(node.children,
                                                            form=f_node.children,
                                                            mappings=mappings,
                                                            exact=True)
                if not does_match:
                    return not_matches
            elif not norm_done:
                if f_node != node:
                    return not_matches
            i += 1
            if i >= len(form):
                break #We've gone past the form
        
        return True, mappings, len(form)