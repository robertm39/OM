import builtin_macros as bm

from node import NodeType
from node import Node
from node import DEF_NODE

BRACKET_DICT = {}
ESCAPE = '`'
WHITESPACE = [' ', '\n', '\t', '\r']

class Bracket:
    def __init__(self, node_type, text):
        self.node_type = node_type
        self.left = text[0]
        self.right = text[1]
        
        BRACKET_DICT[self.left] = self
        BRACKET_DICT[self.right] = self
        
    def __getitem__(self, index):
        return self.left if index == 0 else self.right if index == 1 else None

BRACKET_TYPES = [NodeType.PAREN, NodeType.SQUARE, NodeType.CURLY]

paren = Bracket(NodeType.PAREN, '()')
square = Bracket(NodeType.SQUARE, '[]')
curly = Bracket(NodeType.CURLY, '{}')
BRACKETS = [paren, square, curly]

class Shell:
    def __init__(self):
        self.macros = []
        self.free_macros = {}
        self.bound_macros = {}
        self.current_id = 0
        self.macros_added = 0 #For tracking which macros are older
        for macro in bm.get_builtin_macros(self):
            self.register_macro(macro)

    def take_id(self):
        result = self.current_id
        self.current_id += 1
        return result

    def matching_bracket_index(self, line, ind):
        bracket = line[ind]
        if not bracket in BRACKET_DICT:
            print(bracket)
            raise AssertionError

        bracket_type = BRACKET_DICT[bracket]
        direction = 1 if bracket == bracket_type[0] else -1

        num = 1
        while num != 0 and 0 <= ind < len(line):
            ind = ind + direction
            char = line[ind]
            if ind == 0 or not line[ind-1] in ESCAPE:
                if char == bracket_type[0]:
                    num += direction
                elif char == bracket_type[1]:
                    num -= direction
        if num != 0:
            raise AssertionError
        return ind

    def tokenize(self, line):
        tokens = []

        curr_token = ''
        escaping = 0
        
        ind = 0
        for char in line + ' ':
            if escaping > 0:
                curr_token += char
                escaping -= 1
            elif char in BRACKET_DICT:
                ###Added
                tokens.append(curr_token)
                curr_token = ''
                ###End Added
                curr_token += char
                next_bracket = self.matching_bracket_index(line, ind)
                if next_bracket > ind: #We're at the beginning of a bracket
                    escaping = next_bracket - ind #skip to the next bracket
                else: #We're at the end of a bracket
                    tokens.append(curr_token) #The current token is finished
                    curr_token = ''
            elif char in WHITESPACE:
                tokens.append(curr_token) #We're not escaping, so we're not in brackets
                curr_token = ''
            elif char in ESCAPE:
                curr_token += char
                escaping += 1
            else:
                curr_token += char
            ind += 1 #Update index for next letter
                
        return [t.strip() for t in tokens if t.strip()] #Get rid of whitespace tokens and strip

    def parse(self, token):
        for bracket in BRACKETS:
            if token[0] == bracket[0] and token[-1] == bracket[1]:
                text = token[1:-1]
                child_tokens = self.tokenize(text)
                children = [self.parse(token) for token in child_tokens]
                
                node = Node(bracket.node_type, children=children)
                return node
        if token[0] == '~':
            text = token[1:]
            node = Node(NodeType.CAPTURE, val=text)
            return node
        if token == '->':
            return DEF_NODE
        return Node(NodeType.NORMAL, val=token.replace('`', ''))
    
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
                self.bound_macros[(i, node)] = self.bound_macros.get((i, node), []) + [macro]
    
    def register_macro(self, macro):
        self.macros.append(macro)
        macro.time_added = self.macros_added
        self.macros_added += 1
        
        self.update_bound_and_free(macro)
        self.trim_macros(macro)
        self.sort_macros()

    def sort_macros(self, macros=None):
        if macros==None:
            macros = self.macros
        
        macros.sort(key=lambda m:-m.time_added) #Ascending by age - secondary
        macros.sort(key=lambda m:-len(m.form)) #Descending by length - primary

    def winnow_macros(self, macros, nodes): #Returns unsorted
        poss_macros = [m for m in macros if len(m.form) <= len(nodes)]
        
        max_len = max([len(m.form) for m in poss_macros])
        sure = []
        for i in range(0, len(nodes)):
            #Macros that are completely matched
            done = [m for m in poss_macros if len(m.form) < i + 1]
            sure.extend(done)
            poss_macros = [m for m in poss_macros if not m in done]
            
            if i + 1 > max_len:
                return poss_macros + sure
            free = self.free_macros.get(i, [])
            matching = self.bound_macros.get((i, nodes[i]), [])
            poss_macros = [m for m in poss_macros if m in free or m in matching]
            
            if not poss_macros:
                return sure
            max_len = max([len(m.form) for m in poss_macros])
        return sure + poss_macros

    def apply_macros(self, nodes, verbose=False, level=0): #Takes and returns a list of nodes
        self.sort_macros()
        
        nodes = nodes[:] #Copy to get rid of side effects
        
        changed = False
        
        #Whenever a bracket or macro is evaluated, we go back to the top
        going = True
        while going:
            going = False
            i = 0
            
            for node in nodes: #Interpret inner brackets first
                
                while type(node) is list: #Kludge
                    print('LIST')
                    node = node[0]
                
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
                    self.sort_macros(macros=poss_macros)
                    
                    for macro in poss_macros:
                        matches, captures, length = macro.matches(c_nodes)
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
        tokens = self.tokenize(line)
        if verbose:
            print(tokens)
        nodes = [self.parse(token) for token in tokens] #Parse tokens
        
        if verbose:
            print(nodes)
        
        nodes, changed = self.apply_macros(nodes)
        
        if verbose:
            print('After macros:')
        
        if do_print:
            print(nodes)
            
        if return_nodes:
            return nodes