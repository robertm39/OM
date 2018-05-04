# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:16:39 2018

@author: rober
"""

import om
from utils import normal
from utils import fill_in_form

def handle_cond_macro(form, product_form, cond_form, mappings, shell):
    cond_form = fill_in_form(cond_form, mappings)
    cond, changed = shell.apply_macros(cond_form)
    
    if cond == [normal('True')]:
        return fill_in_form(product_form, mappings)
    else:
        return fill_in_form(form, mappings)

class Macro:
    def __init__(self, form, get_product=None, product_form=None, cond_form=None, shell=None, name='unknown macro'):
        self.form = form
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
    
    #Whether this macro matches the given expression, starting at the left
    def matches(self, expr, form=None, mappings=None, exact=False):
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
            elif f_node.node_type is om.NodeType.PAREN: #A list
                does_match, mappings, length = self.matches(node.children,
                                                            form=f_node.children,
                                                            mappings=mappings,
                                                            exact=True)
                if not does_match:
                    return not_matches
            elif f_node != node:
                return not_matches
            i += 1
            if i >= len(form):
                break #We've gone past the form
        
        return True, mappings, len(form)