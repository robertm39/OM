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
    SLASH = 'SLASH'     #/\
    CAPTURE = 'CAPTURE' #~word
    DEF = 'DEF'         #->
    NORMAL = 'NORMAL'   #word

paren = Bracket(NodeType.PAREN, '()')
square = Bracket(NodeType.SQUARE, '[]')
slash = Bracket(NodeType.SLASH, '/\\')
curly = Bracket(NodeType.CURLY, '{}')
BRACKETS = [paren, square, slash, curly]

def fill_in_form(form, mappings):
    form = form[:]
    
    i = 0
    for node in form:
        if node.node_type is NodeType.CAPTURE:
            name = node.val
            if name in mappings:
                form[i] = mappings[name]
        elif node.node_type in [NodeType.PAREN, NodeType.SQUARE, NodeType.CURLY, NodeType.SLASH]:
            new_node = fill_in_form(node.children, mappings)
            form[i] = new_node
        i += 1
    return form

class Macro:
    def __init__(self, form, get_product=None, product_form=None):
        self.form = form #An expression with only parens, captures, normals, literals and defs (literals not yet implemented)
        if get_product != None:
            self.get_product = get_product
        elif product_form != None:
            self.get_product = lambda mappings: fill_in_form(self.form, mappings)
        else:
            raise AssertionError('No get_product or product_form')
        
    def matches(self, expr, form=None, mappings=None):#Whether this macro matches the given expression, starting at the left
        form = self.form if form == None else form
        mappings = {} if mappings == None else mappings #Captured values: name -> node
        i = 0
        
        not_matches = False, {}, 0
        
        for node in expr:
            to_match = form[i]
            
            if to_match.node_type is NodeType.CAPTURE: #Capture nodes
                name = to_match.val
                if name in mappings: #See whether the node matches the captured node
                    captured_node = mappings[name]
                    if node != captured_node:
                        return not_matches
                else: #Capture this node
                    mappings[name] = node
            elif to_match.node_type is NodeType.PAREN: #A list
                does_match, mappings, length = self.matches(node, form=to_match, mappings=mappings)
                if not does_match:
                    return not_matches
            elif to_match.node_type is NodeType.NORMAL:
                if to_match != node:
                    return not_matches
            elif to_match.node_type is NodeType.DEF:
                if not node.node_type is NodeType.DEF:
                    return not_matches
        
        return True, mappings, len(form)

###Macro has the matches method
###Takes the expression to match
###Returns whether it matches,the captured nodes, and the length of the match
###It may also have side effects for certain built-in macros

###Macro also has the result method
###Takes the captured nodes
###Returns the new expression

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
    
    #TODO __eq__, __neq__
        
DEF_NODE = ParseNode(NodeType.DEF)

class Shell:
    def __init__(self):
        self.macros = {}

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
            print(line, ' ', line[ind], ind, num)
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
                
        return tokens

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

#    def apply_macros(self, tokens): #Takes parsed tokens
#        for token in tokens:
#            if token.node_type is NodeType.NORMAL:
#                if token.val in self.macros:
#                    token.val = self.macros[token.val]
#                    return True
##            if token.node_type 

    def apply_macros(self, nodes): #Takes and returns a list of nodes
        i = 0
        nodes = nodes[:] #Copy to get rid of side effects
        
        changed = False
        
        for node in nodes: #Interpret inner brackets first
            if node.node_type in [NodeType.SQUARE, NodeType.CURLY, NodeType.SLASH]:
                changed = True
                
                insides = node.children
                interpreted = self.apply_macros(insides)
                if node.node_type is NodeType.SQUARE:
                    nodes = nodes[0:i] + interpreted + nodes[i+1:] #Put the result in without brackets
                elif node.node_type is NodeType.CURLY:
                    interpreted = ParseNode(NodeType.PAREN, children=interpreted)
                    nodes = nodes[0:i] + [interpreted] + nodes[i+1:] #Put the result in with paren brackets
                elif node.node_type is NodeType.SLASH:
                    interpreted = ParseNode(NodeType.DONE_SLASH, children=interpreted)
                    nodes = nodes[0:i] + [interpreted] + nodes[i+1:] #Put the result in with done-slash brackets
            i += 1
        #Now the expression has no square, curly or slash brackets
        #Only paren and done-slash
        #Now we can apply macros
        
        for i in range(0, len(nodes)):
            #to_match = nodes[i:]
            for macro in self.macros:
                matches, captures, length = macro.matches(nodes[i:], side_effects=True)
                if matches:
                    changed = True
                    product = macro.get_product(captures)
                    nodes = nodes[0:i] + product + nodes[i+length:]
                i += 1
                
        return nodes, changed

    def interpet(self, line):
        tokens = self.tokenize(line)
        print(tokens)
        nodes = [self.parse(token) for token in tokens] #Parse tokens
        print(nodes)
        
        changed = True
        while changed:
            nodes, changed = self.apply_macros(nodes)
            
        print(nodes)
        #while self.apply_macros(tokens): #Go until no more
        #    pass
        #print(tokens)
        
        
        
        
        
        
        
        
        
        
        
        
        