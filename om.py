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
    CAPTURE = 'CAPTURE' #~*
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
            text = token[1:-1]
            node = ParseNode(NodeType.CAPTURE, val=text)
            return node
        if token == '->':
            return DEF_NODE
        return ParseNode(NodeType.NORMAL, val=token)

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
        
        
        
        
        
        
        
        
        
        
        
        
        