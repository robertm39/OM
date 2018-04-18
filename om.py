from enum import Enum

BRACKET_DICT = {}
ESCAPE = '`'
WHITESPACE = [' ', '\n', '\t', '\r']

class Macro:
    def __init__(self, form, get_product):
        self.form = form #An expression with only parens, captures, normals, literals and defs (literals not yet implemented)
        self.get_product = get_product
        
    def matches(self, expr, form=None, mappings=None):#Whether this macro matches the given expression, starting at the left
        form = self.form if form == None else form
        mappings = {} if mappings == None else mappings #Captured values: name -> node
        i = 0
        for node in expr:
            to_match = form[i]
            
            if to_match.node_type is NodeType.CAPTURE: #Capture nodes
                name = to_match.val
                if name in mappings: #See whether the node matches the captured node
                    captured_node = mappings[name]
                    if node != captured_node:
                        return False
                else: #Capture this node
                    mappings[name] = node
            elif to_match.node_type is NodeType.PAREN: #A list
                does_match, mappings = self.matches(node, form=to_match, mappings=mappings)
                if not does_match:
                    return False
            elif to_match.node_type is NodeType.NORMAL:
                if to_match != node:
                    return False
            elif to_match.node_type is NodeType.DEF:
                if not node.node_type is NodeType.DEF:
                    return False

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

    def apply_macros(self, tokens): #Takes parsed tokens
        for token in tokens:
            if token.node_type is NodeType.NORMAL:
                if token.val in self.macros:
                    token.val = self.macros[token.val]
                    return True
#            if token.node_type 

    def interpet(self, line):
        tokens = self.tokenize(line)
        print(tokens)
        tokens = [self.parse(token) for token in tokens] #Parse tokens
        print(tokens)
        
        #while self.apply_macros(tokens): #Go until no more
        #    pass
        #print(tokens)
        
        
        
        
        
        
        
        
        
        
        
        
        