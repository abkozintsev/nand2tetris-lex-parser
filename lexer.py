from parseTypes import *

#gets input from inputs
def getInput():
    return(open('input.txt', 'r').read())


#valid tokens: symbols, reserved words,  integer constants, string constants, and identifiers
#list of every reserved symbol and word in Jack, from page 182 of textbook.
symbols = {"(",")","[","]","{","}",",",";","=",".","+","-","*","/","&","|","","|","~","<",">"}
keywords = {"class","constructor","method","function","int","boolean","char","void","var","static","field","let","do","if","else","while","return","true","false","null","this"}

#finds the index of the first character not in the token via fsm, by feeding in characters one at time as well as
#the current state into the fsm, until the fsm says that either this or the next character is the final character of the token
def findFirstEnd(file):
    state = 0
    for i in range(len(file)):
        state = fsm(file[i], state)
        #in some cases, such as identifiers and integer constants, we stop on landing on something not in the token, so return i
        #in such instances the fsm returns -1
        if state == -1:
            return i
        #in others, such as strings or symbols, we know that the next character will be the first not in the token, so return i+1
        #in such instances the fsm returns -2
        if state == -2:
            return i+1
    #once the file is "" (all tokens stripped), the file will automatically close before this function is called
    #this fails if the token is unclosed, which should theoretically never happen as any valid program will end in }, a monocharacter token
    #the following line of code should only come up during debugging the parser, it just marks the end of the file as the end of the last token
    #if we somehow got here (probably due to a simplified test case)
    return i+1

#inputs the current character and the current state, determines the state of the next character
#key:
#-2 => next char will be start of next token
#-1 => this char is start of next token
#0 => start of token
#1 => in a string
#11 => in an int
#21 => in a string
#22 => in a string, last character was an unescaped \
#30 => not in anything, previous character was a /, this is either * and we start a block comment, line comment or the token '/' is complete
#300 => in a block comment
#301 => in a block comment, previous character was a *
#310 => in a line comment
#examples:
#fsm('"', 21) == -2, because we are in a string, the current character is a quote, and the last character was not an escape \
#fsm('"', 22) == 21, because we are in a string and though the current character is another quote, the last character escapes it
def fsm(c, state):
    #start of identifier/keyword
    if state == 0 and c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return 1
    #continue identifier/keyword
    elif state == 1:
        if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_":
            return 1
        return -1

    #start of int
    elif state == 0 and c in ("0123456789"):
        return 11
    #continue int
    elif state == 11:
        if c in ("0123456789"):
            return 11
        return -1
    
    #if symbol, we know the next character must be the start of the next token, so return -2 (check for / seperately bcz block comment)
    elif state == 0 and c in symbols and c != '/':
        return -2

    #start of string
    elif state == 0 and c == '"':
        return 21
    #in string, did not just see backslash
    elif state == 21:
        if c == '"':
            return -2
        elif c == '\\':
            return 22
        return 21
    #in string, just saw backslash
    elif state == 22:
        return 21

    #potential start of comment
    elif state == 0 and c == '/':
        return 30
    #start of comment or end of symbol '/'
    elif state == 30:
        #block comment
        if c == '*':
            return 300
        #line comment
        elif c == '/':
            return 310
        #neither of above, so must be symbol '/'
        else:
            return -1
    #in block comment, did not just see *
    elif state == 300:
        if c == '*':
            return 301
        else: 
            return 300
    #in block comment, just saw *
    elif state == 301:
        if c == '/':
            return -2
        else:
            return 300
    #line comment handling
    elif state == 310:
        if c == '\n':
            return -1
        else:
            return 310
    elif c == ' ':
        return -2

#fileTokenize :: String -> [String]
#input: the entire file as a string with all \n removed
#output: all tokens w/o classification, e.g. ['if', '(', 'x', '<', '0', ')', '{']
#converts the file into tokens via appending the first token of the file to a list
#then recursively appending the first token of the rest of the file to the list until the rest of the file is "", at which point
#end recursion
def fileTokenizeRaw(rawInput):
    rawInput = rawInput.strip()
    if rawInput == "":
        return []
    else:
        firstEnd = findFirstEnd(rawInput)
        if firstEnd == -1:
            return []
        token = rawInput[0:firstEnd]
        if token == ' ' or token == '\r\n' or (len(token) > 1 and token[0] == '/'):
            token = []
        else:
            token = [token]
        rest = rawInput[firstEnd:]
        return token + fileTokenizeRaw(rest)

#fileTokenizeRaw :: [String] -> [String]
#input: multiple lines of Jack
#output: one long list of tokens
#converts the file into unclassified tokens

#tokenClassifier :: String -> Token
#Inputs (each a seperate call): if, 5, hello, "5"
#Outputs: different objects with those values
#determines type of token
def tokenClassifier(token):
    if token in symbols:
        if token == '<':
            return (Symbol("&lt;"))
        elif token == '>': 
            return (Symbol("&gt;"))
        elif token == "&":
            return (Symbol("&amp;"))
        return(Symbol(token))
    elif token in keywords:
        return(Keyword(token))
    elif token[0] in "0123456789":
        return(IntegerConstant(int(token)))
    elif token[0] == '"':
        return(StringConstant(token[1:-1]))
    else:
        return(Identifier(token))

#lexer :: [input file] -> [Token]
def lex(rawInput):
    out = []
    rawTokens = fileTokenizeRaw(rawInput)
    for token in rawTokens:
        out.append(tokenClassifier(token))
    return out

def test():
    rawInput = getInput()
    tokens = lex(rawInput)
    print(tokens)
