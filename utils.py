# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:17:43 2018

@author: rober
"""

import om
from node import Node
from node import NodeType

def fill_in_form(form, mappings):
    form = form[:]
    
    i = 0
    for node in form:
        if node.node_type is NodeType.CAPTURE:
            name = node.val
            if name in mappings:
                form[i] = mappings[name]
        elif node.node_type in om.BRACKET_TYPES:
            new_nodes = fill_in_form(node.children, mappings)
            form[i] = Node(node.node_type, children=new_nodes)
        i += 1
        
    return form

def normal(val):
    return Node(NodeType.NORMAL, val=val)

def capture(val):
    return Node(NodeType.CAPTURE, val=val)

def unpack_and_wrap_node(node):
    if node.node_type is NodeType.PAREN:
        return node.children
    return [node]