from enum import Enum

#BRACKETS = ['()', '[]', '<>', '/\\', '{}']
#for bracket in BRACKETS:
#    BRACKET_DICT[bracket[0]] = bracket
#    BRACKET_DICT[bracket[1]] = bracket

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
    ANGLE = 'ANGLE'     #<>
    SLASH = 'SLASH'     #/\
    CAPTURE = 'CAPTURE' #{}
    DEF = 'DEF'         #->
    NORMAL = 'NORMAL'   #word

Bracket(NodeType.PAREN, '()')
Bracket(NodeType.SQUARE, '[]')
Bracket(NodeType.SLASH, '/\\')
Bracket(NodeType.ANGLE, '<>')

class ParseNode:
    def __init__(self, node_type, val='', children=[]):
        self.node_type = node_type
        self.val = val
        self.children = children[:]

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
        if token[0] == '(' and token[-1] == ')':
            inside = token[1:-1] #Withouth the parens
            node = ParseNode(NodeType.PAREN, val=inside)

    def interpet(self, line):
        tokens = self.tokenize(line)
        
        if tokens[1] == '->':
            pass
        
        
        
        
        
        
        
        
        
        
        
        
        