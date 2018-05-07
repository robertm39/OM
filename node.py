# -*- coding: utf-8 -*-
"""
Created on Fri May  4 15:32:40 2018

@author: rober
"""

from enum import Enum

class NodeType(Enum):
    PAREN = 'PAREN'     #()
    SQUARE = 'SQUARE'   #[]
    CURLY = 'CURLY'     #{}
    CAPTURE = 'CAPTURE' #~word
#    DEF = 'DEF'         #->
    NORMAL = 'NORMAL'   #word
    
class Node:
    def __init__(self, node_type, val='', children=[]):
        self.node_type = node_type
        self.val = val
        self.children = children[:]
        
    def __str__(self, depth=0):
        result = '(' + str(self.node_type)[9:] + ' ' + str(self.val) + ')'
        result = result[0] + result[1:-1].strip() + result[-1] #Get rid of internal edge whitespace
        result = '\t' * depth + result + '\n'
        for child in self.children:
            result += child.__str__(depth=depth+1)
        
        return result
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if other == None:
            return False
        if self.val != other.val:
            return False
        if self.children != other.children:
            return False
        if self.node_type != other.node_type:
            return False
        if hasattr(self, 'id') != hasattr(other, 'id'):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            if self.id != other.id:
                return False
        return True
    
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        result = 17
        result += hash(self.val)
        result *= 31
        result += hash(self.id) if hasattr(self, 'id') else 0
        result *= 31
        return result
        
#DEF_NODE = Node(NodeType.DEF)
DEF_NODE = Node(NodeType.NORMAL, val='->')