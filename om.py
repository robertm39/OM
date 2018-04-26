from enum import Enum

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

class NodeType(Enum):
    PAREN = 'PAREN'     #()
    SQUARE = 'SQUARE'   #[]
    CURLY = 'CURLY'     #{}
    CAPTURE = 'CAPTURE' #~word
    DEF = 'DEF'         #->
    NORMAL = 'NORMAL'   #word

BRACKET_TYPES = [NodeType.PAREN, NodeType.SQUARE, NodeType.CURLY]

paren = Bracket(NodeType.PAREN, '()')
square = Bracket(NodeType.SQUARE, '[]')
curly = Bracket(NodeType.CURLY, '{}')
BRACKETS = [paren, square, curly]

def fill_in_form(form, mappings):
#    print('fill_in_form running')
#    print(form)
#    print('')
    form = form[:]
#    print(form)
#    print('')
    
    i = 0
    for node in form:
        if node.node_type is NodeType.CAPTURE:
            name = node.val
            if name in mappings:
                form[i] = mappings[name]
        elif node.node_type in BRACKET_TYPES:#, NodeType.SLASH]:
            new_nodes = fill_in_form(node.children, mappings)
            form[i] = ParseNode(node.node_type, children=new_nodes)
#            new_node = fill_in_form(node.children, mappings)
#            form[i] = new_node
        i += 1
#    print(form)
#    print('***')
    return form

class Macro:
    def __init__(self, form, get_product=None, product_form=None, name='unknown macro'):
        self.form = form #An expression with only parens, captures, normals, literals and defs (literals not yet implemented)
        self.name=name
        
        if get_product != None:
            self.get_product = get_product
        elif product_form != None:
#            print('Going by product_form')
#            print(product_form)
#            print('***')
            self.get_product = lambda mappings: fill_in_form(product_form, mappings)
        else:
            raise AssertionError('No get_product or product_form')
    
    def __str__(self):
        return self.name
    
    def matches(self, expr, form=None, mappings=None, exact=False):#Whether this macro matches the given expression, starting at the left
#        print('matches running')
        
        form = self.form if form == None else form
        mappings = {} if mappings == None else mappings #Captured values: name -> node
        i = 0
        
        not_matches = False, {}, 0
        
#        print('expr:')
#        print(expr)
#        print('***')
        
        if len(expr) < len(form):
            return not_matches
        
        #For an exact match, the expr and the form must be the same length
        if exact and len(expr) > len(form):
            print('EXACT FAIL')
            return not_matches
        
#        print('Checking nodes')
        for node in expr:
            if node.val == '|': #blocks macro comprehension
                return not_matches
            
            to_match = form[i]
#            print(node)
#            print(to_match)
#            print('***')
            
            if to_match.node_type is NodeType.CAPTURE: #Capture nodes
                name = to_match.val
                if name in mappings: #See whether the node matches the captured node
                    captured_node = mappings[name]
                    if node != captured_node:
                        return not_matches
                else: #Capture this node
                    mappings[name] = node
            elif to_match.node_type is NodeType.PAREN: #A list
                does_match, mappings, length = self.matches(node.children, form=to_match.children, mappings=mappings, exact=True)
                if not does_match:
                    return not_matches
            elif to_match.node_type is NodeType.NORMAL:
                if to_match != node:
                    return not_matches
            elif to_match.node_type is NodeType.DEF:
                if not node.node_type is NodeType.DEF:
                    return not_matches
            i += 1
            if i >= len(form):
                break #We've gone past the form
        
        return True, mappings, len(form)

###Built-in macros
def unpack_and_wrap_node(node):
    if node.node_type is NodeType.PAREN:
        return node.children
    return [node]
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
    form = [ParseNode(NodeType.CAPTURE, val='FORM'), DEF_NODE, ParseNode(NodeType.CAPTURE, val='PRODUCT')]
    return Macro(form=form,
                 name='DEFMAC',
                 get_product=lambda maps: defmac_get_product(shell, maps))
#********************
def loc_macro_get_product(shell, mappings):
    def make_local(name, node_id, prog): #Modifies the passed object
        for node in prog:
            if node.node_type is NodeType.NORMAL:
                if node.val == name:
                    node.id = node_id #Make into a local node
            if node.node_type in BRACKET_TYPES:
                make_local(name, node_id, node.children)
    
    node_id = shell.take_id()
    name = mappings['name'].val
    prog = mappings['prog'].children
    make_local(name, node_id, prog)
    return prog

def get_loc_macro(shell):
    form = [ParseNode(NodeType.NORMAL, val='loc'),
            ParseNode(NodeType.CAPTURE, val='name'),
            ParseNode(NodeType.CAPTURE, val='prog')]
    return Macro(form=form,
                 name='LOC',
                 get_product = lambda maps: loc_macro_get_product(shell, maps))
#********************
def to_bool_get_product(mappings): #Improve
    node = mappings['a']
    t_node = [ParseNode(NodeType.NORMAL, val='True')]
    f_node = [ParseNode(NodeType.NORMAL, val='False')]
    if node.node_type is NodeType.PAREN:
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
    form = [ParseNode(NodeType.NORMAL, val='bool'), ParseNode(NodeType.CAPTURE, val='a')]
    return Macro(form=form, name='TO_BOOL', get_product=to_bool_get_product)
#********************
def binary_macro_get_product(mappings, op):
    v1 = mappings['a'].val
    v2 = mappings['b'].val
    
    val = op(v1, v2)
    return [ParseNode(NodeType.NORMAL, val=str(val))]

def get_binary_macro(name, op):
    form = [ParseNode(NodeType.CAPTURE, val='a'),
            ParseNode(NodeType.NORMAL, val=name),
            ParseNode(NodeType.CAPTURE, val='b')]
    
    return Macro(form=form,
                 name=name,
                 get_product=lambda maps: binary_macro_get_product(maps, op))

#********************
def print_macro_get_product(mappings):
    node = mappings['a']
    print(node.val)
    return []

def get_print_macro():
    form = [ParseNode(NodeType.NORMAL, val='pr'), ParseNode(NodeType.CAPTURE, val='a')]
    return Macro(form=form, name='pr', get_product=print_macro_get_product)
#********************
def ind_macro_get_product(mappings):
    i = int(float(mappings['i'].val))
    l = mappings['l'].children
    return [l[i]]

def get_ind_macro():
    form = [ParseNode(NodeType.NORMAL, val='ind'),
            ParseNode(NodeType.CAPTURE, val='i'),
            ParseNode(NodeType.CAPTURE, val='l')]
    return Macro(form=form, name='ind', get_product=ind_macro_get_product)

#********************
def unw_macro_get_product(mappings):
    node = mappings['a']
    return node.children

def get_unw_macro():
    form = [ParseNode(NodeType.NORMAL, val='unw'), ParseNode(NodeType.CAPTURE, val='a')]
    return Macro(form=form, name='unw', get_product=unw_macro_get_product)
#********************
def len_macro_get_product(mappings):
    node = mappings['l']
    return [ParseNode(NodeType.NORMAL, val=str(len(node.children)))]

def get_len_macro():
    form = [ParseNode(NodeType.NORMAL, val='len'), ParseNode(NodeType.CAPTURE, val='l')]
    return Macro(form=form, name='len', get_product=len_macro_get_product)
#********************
def get_builtin_macros(shell):
    return [get_defmac_macro(shell),
            get_loc_macro(shell),
            get_to_bool_macro(),
            get_print_macro(),
            get_ind_macro(),
            get_unw_macro(),
            get_len_macro(),
            get_binary_macro('+', lambda a,b:float(a) + float(b)),
            get_binary_macro('-', lambda a,b:float(a) - float(b)),
            get_binary_macro('*', lambda a,b:float(a) * float(b)),
            get_binary_macro('**', lambda a,b:float(a) ** float(b)),
            get_binary_macro('%', lambda a,b:float(a) % float(b)),
            get_binary_macro('/', lambda a,b:float(a) / float(b)),
            get_binary_macro('>', lambda a,b:float(a) > float(b)),
            get_binary_macro('<', lambda a,b:float(a) < float(b)),
            get_binary_macro('>=', lambda a,b:float(a) >= float(b)),
            get_binary_macro('<=', lambda a,b:float(a) <= float(b))]
###End Built-in macros


class ParseNode:
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
        if self.node_type != other.node_type:
            return False
        if self.val != other.val:
            return False
        if self.children != other.children:
            return False
        if hasattr(self, 'id') != hasattr(other, 'id'):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            if self.id != other.id:
                return False
        return True
    
    def __ne__(self, other):
        return not self == other
        
DEF_NODE = ParseNode(NodeType.DEF)

class Shell:
    def __init__(self):
#        self.macros = get_builtin_macros(self)
        self.macros = []
        self.current_id = 0
        self.macros_added = 0 #For tracking which macros are older
        for macro in get_builtin_macros(self):
            self.register_macro(macro)
        
#        print(self.macros)

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
#            print(line, ' ', line[ind], ind, num)
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
                
                node = ParseNode(bracket.node_type, children=children)
                return node
        if token[0] == '~':# and token[-1] == '}': #Technically not a bracket
            text = token[1:]
            node = ParseNode(NodeType.CAPTURE, val=text)
            return node
        if token == '->':
            return DEF_NODE
        return ParseNode(NodeType.NORMAL, val=token.replace('`', ''))

    def register_macro(self, macro):
        self.macros.append(macro)
        macro.time_added = self.macros_added
        self.macros_added += 1
        
        self.sort_macros()

    def sort_macros(self):
        self.macros.sort(key=lambda m:-m.time_added) #Ascending by age - secondary
        self.macros.sort(key=lambda m:-len(m.form)) #Descending by length - primary

    def apply_macros(self, nodes, verbose=False): #Takes and returns a list of nodes
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
                    interpreted, changed = self.apply_macros(insides)
                    if node.node_type is NodeType.SQUARE:
                        nodes = nodes[0:i] + list(interpreted) + nodes[i+1:] #Put the result in without brackets
                    elif node.node_type is NodeType.CURLY:
                        interpreted = ParseNode(NodeType.PAREN, children=interpreted)
                        nodes = nodes[0:i] + [interpreted] + nodes[i+1:] #Put the result in with paren brackets
                    break
                i += 1
            #Now the expression has no outer square or curly brackets
            #Only paren
            #So now we can apply macros
            if not going:
                for macro in self.macros: #Now the macros will be gone through in order
                    for i in range(0, len(nodes)): #going through nodes
                        matches, captures, length = macro.matches(nodes[i:])
                        if matches:
                            going = True
                            changed = True
                            product = macro.get_product(captures)
                            if verbose:
                                print('***** ' + macro.name + ' *****')
                                print(nodes)
                            nodes = nodes[0:i] + product + nodes[i+length:]
                            if verbose:
                                print('*****')
                                print(nodes)
                                print('*' * (12 + len(macro.name)))
                                print('')
                            break #Go back to the smallest macros
                    if going:
                        break
                
        return nodes, changed

    def interpret(self, line, verbose=False):
        tokens = self.tokenize(line)
        if verbose:
            print(tokens)
        nodes = [self.parse(token) for token in tokens] #Parse tokens
        
        if verbose:
            print(nodes)
        
        nodes, changed = self.apply_macros(nodes)
        
        if verbose:
            print('After macros:')
            
        print(nodes)