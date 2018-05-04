# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:03:13 2018

@author: rober
"""
import om
import node as nd

from macro import Macro
from utils import unpack_and_wrap_node
from utils import normal
from utils import capture

#********************
def defmac_get_product(shell, mappings):
    
    form = mappings['FORM']
    product_form = mappings['PRODUCT']
    
    form = unpack_and_wrap_node(form)
    product_form = unpack_and_wrap_node(product_form)
    
    shell.register_macro(Macro(form, product_form=product_form))
    shell.sort_macros() #Should add method to Shell for adding and sorting together
    return [] #Evaluates to nothing

def get_defmac_macro(shell):
    form = [capture('FORM'),
            om.DEF_NODE,
            capture('PRODUCT')]
    return Macro(form=form,
                 name='DEFMAC',
                 get_product=lambda maps: defmac_get_product(shell, maps))
#********************
def def_condmac_get_product(shell, mappings):
    form = mappings['FORM']
    product_form = mappings['PRODUCT']
    cond = mappings['COND']
    
    form = unpack_and_wrap_node(form)
    product_form = unpack_and_wrap_node(product_form)
    cond = unpack_and_wrap_node(cond)
    
    shell.register_macro(Macro(form,
                               product_form=product_form,
                               cond_form=cond,
                               shell=shell))
    
    return [] #Evaluates to nothing
    
def get_def_condmac_macro(shell):
    form = [capture('FORM'),
            om.DEF_NODE,
            capture('PRODUCT'),
            normal('if'),
            capture('COND')]
    return Macro(form=form,
                 name='DEF_CONDMAC',
                 get_product=lambda maps: def_condmac_get_product(shell, maps))
#********************
def loc_macro_get_product(shell, mappings):
    def make_local(names, node_id, prog): #Modifies the passed object
        for name in names:
            for node in prog:
                if node.node_type is om.NodeType.NORMAL:
                    if node.val == name:
                        if not hasattr(node, 'id'):
                            node.id = node_id #Make into a local node
                if node.node_type in om.BRACKET_TYPES:
                    make_local(name, node_id, node.children)
    
    node_id = shell.take_id()
    names = unpack_and_wrap_node(mappings['names'])
    names = [node.val for node in names]
    prog = mappings['prog'].children
    make_local(names, node_id, prog)
    return prog

def get_loc_macro(shell):
    form = [normal('loc'),
            capture('names'),
            capture('prog')]
    return Macro(form=form,
                 name='LOC',
                 get_product = lambda maps: loc_macro_get_product(shell, maps))
#********************
def to_bool_get_product(mappings): #Improve
    node = mappings['a']
    t_node = [normal('True')]
    f_node = [normal('False')]
    if node.node_type is om.NodeType.PAREN:
        return t_node if node.children else f_node
    if node in [t_node[0], f_node[0]]: #False and True evaluate to themselves
        return [node]
    try:
        if float(node.val):
            return t_node
        else:
            return f_node
    except ValueError:
        pass
    return t_node

def get_to_bool_macro():
    form = [normal('bool'),
            capture('a')]
    return Macro(form=form, name='TO_BOOL', get_product=to_bool_get_product)
#********************
def binary_macro_get_product(mappings, op):
    v1 = mappings['a'].val
    v2 = mappings['b'].val
    
    val = op(v1, v2)
    return [normal(str(val))]

def get_binary_macro(name, op):
    form = [capture('a'),
            normal(name),
            capture('b')]
    
    return Macro(form=form,
                 name=name,
                 get_product=lambda maps: binary_macro_get_product(maps, op))

#********************
def print_macro_get_product(mappings):
    node = mappings['a']
    print(node.val)
    return []

def get_print_macro():
    form = [normal('pr'),
            capture('a')]
    return Macro(form=form, name='pr', get_product=print_macro_get_product)
#********************
def ind_macro_get_product(mappings):
    i = int(float(mappings['i'].val))
    l = mappings['l'].children
    return [l[i]]

def get_ind_macro():
    form = [normal('ind'),
            capture('i'),
            capture('l')]
    return Macro(form=form, name='ind', get_product=ind_macro_get_product)

#********************
def unw_macro_get_product(mappings):
    node = mappings['a']
    return node.children

def get_unw_macro():
    form = [normal('unw'),
            capture('a')]
    return Macro(form=form, name='unw', get_product=unw_macro_get_product)
#********************
def len_macro_get_product(mappings):
    node = mappings['l']
    return [normal(str(len(node.children)))]

def get_len_macro():
    form = [normal('len'),
            capture('l')]
    return Macro(form=form, name='len', get_product=len_macro_get_product)
#********************
def expd_macro_get_product(mappings):
    a = mappings['a']
    result = []
    for char in a.val:
        result.append(normal(char))
    return [nd.Node(nd.NodeType.PAREN, children=result)]

def get_expd_macro():
    form = [normal('expd'),
            capture('a')]
    return Macro(form=form, name='expd', get_product=expd_macro_get_product)
#********************
def wrap_macro_get_product(mappings):
    l = mappings['l']
    result = ''
    for node in l.children:
        result += node.val
    return [normal(result)]

def get_wrap_macro():
    form = [normal('wrap'),
            capture('l')]
    return Macro(form=form, name='wrap', get_product=wrap_macro_get_product)
#********************
def inp_macro_get_product(mappings):
    val = input('IN:')
    return [normal(val)]

def get_inp_macro():
    form = [normal('inp')]
    return Macro(form=form, name='inp', get_product=inp_macro_get_product)
#********************
def char_macro_get_product(mappings):
    a = mappings['a']
    val = chr(int(float(a.val)))
    return [normal(val)]

def get_char_macro():
    form = [normal('char'),
            capture('a')]
    return Macro(form=form, name='char', get_product=char_macro_get_product)
#********************
def ord_macro_get_product(mappings):
    a = mappings['a']
    val = ord(a.val[0])
    return [normal(val)]

def get_ord_macro():
    form = [normal('ord'),
            capture('a')]
    return Macro(form=form, name='ord', get_product=ord_macro_get_product)
#********************
def get_builtin_macros(shell):
    return [get_defmac_macro(shell),
            get_def_condmac_macro(shell),
            get_loc_macro(shell),
            get_to_bool_macro(),
            get_print_macro(),
            get_ind_macro(),
            get_unw_macro(),
            get_len_macro(),
            get_expd_macro(),
            get_wrap_macro(),
            get_inp_macro(),
            get_char_macro(),
            get_ord_macro(),
            get_binary_macro('+', lambda a,b:float(a) + float(b)),
            get_binary_macro('-', lambda a,b:float(a) - float(b)),
            get_binary_macro('*', lambda a,b:float(a) * float(b)),
            get_binary_macro('**', lambda a,b:float(a) ** float(b)),
            get_binary_macro('%', lambda a,b:float(a) % float(b)),
            get_binary_macro('/', lambda a,b:float(a) / float(b)),
            get_binary_macro('>', lambda a,b:float(a) > float(b)),
            get_binary_macro('<', lambda a,b:float(a) < float(b)),
            get_binary_macro('>=', lambda a,b:float(a) >= float(b)),
            get_binary_macro('<=', lambda a,b:float(a) <= float(b)),
            get_binary_macro('f-eq', lambda a,b:float(a) == float(b)),
            get_binary_macro('f-neq', lambda a,b:float(a) != float(b))]
###End Built-in macros