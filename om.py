import builtin_macros as bm

from node import NodeType
from node import Node

from utils import BRACKET_TYPES
import utils

class Shell:
    def __init__(self):
        self.macros = []
        self.max_len = 0
        self.free_macros = {}  #index -> list
        self.bound_macros = {} #(index, val) -> list
        self.current_id = 1
        self.macros_added = 0 #For tracking which macros are older
        for macro in bm.get_builtin_macros(self):
            self.register_macro(macro)

    def take_id(self):
        result = self.current_id
        self.current_id += 1
        return result

    def trim_macros(self, newest):
        if not newest.is_cond:
            length = len(newest.form)
            l_macros = [m for m in self.macros if len(m.form) == length]
            l_macros.remove(newest)
            for macro in l_macros:
                #newest would match anything macro would
                if newest.matches(macro.form)[0]:
                    self.macros.remove(macro)
    
    def update_bound_and_free(self, macro):
        for i in range(0, len(macro.form)):
            node = macro.form[i]
            #I don't want to recursively deal with brackets right now, this'll do
            if node.node_type is NodeType.CAPTURE or node.node_type in BRACKET_TYPES:
                if not i in self.free_macros:
                    self.free_macros[i] = [macro]
                else:
                    self.free_macros[i].append(macro)
            else:
#                self.bound_macros[(i, node.val)] = self.bound_macros.get((i, node.val), []) + [macro]
                self.bound_macros[(i, node.val, node.id)] = self.bound_macros.get((i, node.val, node.id), []) + [macro]
    
    def update_max_len(self, macro):
        self.max_len = max(self.max_len, macro.ln)
    
    def register_macro(self, macro):
        self.macros.append(macro)
        macro.time_added = self.macros_added
        self.macros_added += 1
        
        self.update_bound_and_free(macro)
        self.trim_macros(macro)
        self.update_max_len(macro)

    def sort_macros(self, macros=None):
        if macros==None:
            macros = self.macros
        
        macros.sort(key=lambda m:-m.time_added) #Ascending by age - secondary
        macros.sort(key=lambda m:-m.ln) #Descending by length - primary
    
    def matches(self, macro, nodes, i):
        form = macro.form
        return macro.ln <= i or form[i].node_type is NodeType.CAPTURE or form[i].node_type in BRACKET_TYPES or form[i] == nodes[i]
    
    def winnow_macros(self, macros, nodes): #Returns unsorted
        n_len = len(nodes)
        if n_len < self.max_len:
            max_len = min(n_len, self.max_len)
        else:
            max_len = self.max_len
        
        result = None
        poss_macros = macros[:]
        sure = []
        for i in range(0, n_len):
            #Macros that are completely matched
            done = [m for m in poss_macros if m.ln == i]
            sure.extend(done)
            
            for m in done:
                poss_macros.remove(m)
            
            if i + 1 > max_len:
                result = sure + poss_macros
                break
            
            free = self.free_macros.get(i, [])
#            matching = self.bound_macros.get((i, nodes[i].val), [])
            matching = self.bound_macros.get((i, nodes[i].val, nodes[i].id), [])#Added id
            left = set(free) | set(matching)
            poss_macros = list(set(poss_macros) & left)
            
            if not poss_macros:
                result = sure
                break
            max_len = max([m.ln for m in poss_macros])
            
        if not result:
            result = sure + poss_macros
            
        result = [m for m in result if m.ln <= n_len]
        
        return result
    
    def apply_macros(self, nodes, verbose=False, level=0): #Takes and returns a list of nodes
        
        nodes = nodes[:] #Copy to get rid of side effects
        
        changed = False
        
        #Whenever a bracket or macro is evaluated, we go back to the top
        going = True
        while going:
            going = False
            i = 0
            
            for node in nodes: #Interpret inner brackets first
                
                if node.node_type in [NodeType.SQUARE, NodeType.CURLY]:
                    changed = True
                    going = True
                    
                    insides = node.children
                    interpreted, changed = self.apply_macros(insides, level=level+1)
                    if node.node_type is NodeType.SQUARE:
                        nodes = nodes[0:i] + list(interpreted) + nodes[i+1:] #Put the result in without brackets
                    elif node.node_type is NodeType.CURLY:
                        interpreted = Node(NodeType.PAREN, children=interpreted)
                        nodes = nodes[0:i] + [interpreted] + nodes[i+1:] #Put the result in with paren brackets
                    break
                i += 1
            #Now the expression has no outer square or curly brackets
            #Only paren
            #So now we can apply macros
            if not going:
                
                for i in range(0, len(nodes)):
                    
                    c_nodes = nodes[i:]
                    poss_macros = self.winnow_macros(self.macros, c_nodes)
                    
                    #Sort poss_macros
                    if len(poss_macros) > 2:
                        self.sort_macros(macros=poss_macros)
                    else:
                        if len(poss_macros) == 2:
                            if poss_macros[1] < poss_macros[0]:
                                poss_macros = poss_macros[::-1]
                    
                    for macro in poss_macros:
                        matches, captures, length = macro.matches(c_nodes, norm_done=True)
                        if matches:
                            product = macro.get_product(captures)
                            if product != nodes[i:i+length]:#Only if changed
                                going = True
                                changed = True
                                if verbose:
                                    print('***** ' + macro.name + ' *****')
                                    print(nodes)
                                nodes = nodes[0:i] + product + nodes[i+length:]
                                if verbose:
                                    print('*****')
                                    print(nodes)
                                    print('*' * (12 + len(macro.name)))
                                    print('')
                                break #Go back to brackets
                                
                    if going:
                        break
                
        return nodes, changed

    def interpret(self, line, verbose=False, do_print=False, return_nodes=False):
        tokens = utils.tokenize(line)
        if verbose:
            print(tokens)
        nodes = [utils.parse(token) for token in tokens] #Parse tokens
        
        if verbose:
            print(nodes)
        
        nodes, changed = self.apply_macros(nodes)
        
        if verbose:
            print('After macros:')
        
        if do_print:
            print(nodes)
            
        if return_nodes:
            return nodes