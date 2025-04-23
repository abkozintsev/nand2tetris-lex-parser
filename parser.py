from parseTypes import *
from lexer import *
import xml.dom.minidom

#generally, this code by descending from the top to the bottom, calling different compile functions

#implements 'class' className '{' classVarDec* subroutineDec* '}'
def compileClass(tokens, index):
    name = Name(tokens[1])
    endOfClass = findClosingBracket(tokens, index, '{', '}')
    (classVarDecs,index) = compileClassVarDecs(tokens,index+3)
    (subroutineDecsRaw,index) = findSubroutines(tokens, index-1)
    subroutineDecs = list(map(compileSubroutineDec, subroutineDecsRaw))
    return(JackClass(name,classVarDecs,subroutineDecs), endOfClass)

#tested
def compileClassVarDecs(tokens,index):
    (classVarDecsRaw, startSubroutines) = findList(tokens,index,lambda x: x == Symbol(';'),lambda x: x in [Keyword("constructor"),Keyword("function"),Keyword("method")])
    classVarDecs = []
    if len(classVarDecsRaw[0]) > 0:
        classVarDecs = list(map(compileClassVarDec,classVarDecsRaw))
    return(classVarDecs, startSubroutines)

#compiles varDec subroutine
#tested
def compileClassVarDec(varDecRaw):
    if varDecRaw[0] not in [Keyword("static"),Keyword("field")]:
        raise Exception(f"Error: invalid class variable declaration, expected static or field, found {varDecRaw[0]}")
    jackType = JackType(varDecRaw[1])
    names = []
    for i in range(2, len(varDecRaw), 2):
        names.append(Name(varDecRaw[i]))
    return ClassVarDec(varDecRaw[0],jackType,names)

#determines type
#tested
def compileType(token):
    if token in [Keyword("int"),Keyword("char"),Keyword("boolean"), Keyword("void")]:
        return JackType(token)
    elif type(token) == Identifier:
        return JackType(Name(token))
    else:
        raise Exception(f"Error: {token} is an invalid type")

#finds a list of possible phrases given conditions to seperate phrases and to end list
#tested
def findList(tokens, start,seperateCond,endCond):
    if len(tokens) == 0:
        return(([], 1))
    i = start
    startOfExp = start
    state = 0
    exps = []
    while state != -2:
        if i >= len(tokens) and i == 1:
            return(exps, i)
        state = fsm_finder(state, tokens[i],seperateCond,endCond)
        i += 1
        if state == -1:
            exps.append(tokens[startOfExp:i-1])
            startOfExp = i
    if state == -2:
        exp = tokens[startOfExp:i-1]
        if len(exp) > 0:
            exps.append(exp)
    return((exps,i))
def fsm_finder(state, token, seperateCond, endCond):
    if state == 0 and seperateCond(token):
        return(-1)
    elif endCond(token):
        return(-2)
    return 0

#tested
def findSubroutines(tokens, index):
    subroutines = []
    i = index
    while (i < len(tokens)):
        if tokens[i] in [Keyword('constructor'),Keyword('function'),Keyword('method')]:
            start = i
            i = findClosingBracket(tokens,i, '{', '}')+1
            subroutines.append(tokens[start:i])
            continue
        break
    return (subroutines,i)

#tested
def compileSubroutineDec(subroutineDecRaw):
    conFunMet = subroutineDecRaw[0]
    jackType = JackType(subroutineDecRaw[1])
    name = SubroutineName(subroutineDecRaw[2])
    (parameterList, startBod) = findList(subroutineDecRaw,4,lambda x: x == Symbol(','),lambda x: x == Symbol(')'))
    subroutineBody = compileSubroutineBody(subroutineDecRaw[startBod:len(subroutineDecRaw)],0)
    return(SubroutineDec(conFunMet,jackType,name,parameterList,subroutineBody))
    
#tested
def compileSubroutineBody(tokens, start):
    end = findClosingBracket(tokens,start, '{', '}')
    subBodRaw = tokens[start:end]
    (varDecsRaw,startStatements) = findList(tokens, 1, lambda x: x == Symbol(";"), lambda x: x in [Keyword('let'),Keyword('if'),Keyword('while'),Keyword('do'),Keyword('return')])
    startStatements -= 1
    varDecs = list(map(compileVarDec,varDecsRaw))
    statements = compileStatements(subBodRaw[startStatements:end], 0)
    return SubroutineBody(varDecs, statements)

#tested
def compileStatements(tokens, start):
    i = start
    endBod = len(tokens)
    statements = []
    while (i != endBod):
        if tokens[i] == Keyword("let"):
            start = i
            end = findEoS(tokens, start)
            statements.append(compileLet(tokens[start:end+1]))
        elif tokens[i] == Keyword("if"):
            start = i
            end = findClosingBracket(tokens, i, '{', '}')
            if tokens[end+1] == Keyword("else"):
                end = findClosingBracket(tokens, end+1, '{', '}')
            statements.append(compileIf(tokens[start:end+1]))
        elif tokens[i] == Keyword("while"):
            start = i
            end = findClosingBracket(tokens, i, '{', '}')
            statements.append(compileWhile(tokens[start:end+1]))
        elif tokens[i] == Keyword("do"):
            start = i
            end = findEoS(tokens, start)
            statements.append(compileDo(tokens[start:end+1]))
        elif tokens[i] == Keyword("return"):
            start = i
            end = findEoS(tokens, start)
            statements.append(compileReturn(tokens[start:end+1]))
        else:
            raise Exception(f"Error: attempted to compile invalid statement, {tokens[i]} cannot be beginning of new statement.")
        i = end+1
    return(statements)

#tested
def compileLet(tokens):
    name = Name(tokens[1])
    if tokens[2] == Symbol('['):
        startExp1 = 2
        endExp1 = findClosingBracket(tokens, 2, '[', ']')
        expression1 = compileExp(tokens[startExp1:endExp1+1],0)
        startExp2 = endExp1+2
    else:
        expression1 = []
        startExp2 = 3
    expression2 = compileExp(tokens[startExp2:len(tokens)-1],0)
    return(LetStatement(name, expression1, expression2))

#tested
def compileIf(tokens):
    startExp = 2
    endExp = findClosingBracket(tokens,1,'(',')')
    expression = compileExp(tokens[startExp:endExp], 0)
    startStates1 = endExp + 2
    endStates1 = findClosingBracket(tokens,endExp+1,'{','}')
    statements1 = compileStatements(tokens[startStates1:endStates1], 0)
    if endStates1 == len(tokens)-1:
        statements2 = []
    else:
        startStates2 = endStates1+3
        endStates2 = len(tokens)-1
        statements2 = compileStatements(tokens[startStates2:endStates2], 0)
    return(IfStatement(expression, statements1, statements2))

#tested
def compileWhile(tokens):
    startExp = 2
    endExp = findClosingBracket(tokens,1,'(',')')
    expression = compileExp(tokens[startExp:endExp], 0)
    startStates = endExp+2
    endStates = findClosingBracket(tokens,endExp+1,'{','}')
    
    statements = compileStatements(tokens[startStates:endStates], 0)
    return(WhileStatement(expression, statements))

#tested
def compileDo(tokens):
    start = 1
    end = len(tokens)-1
    return DoStatement(compileSubroutineCall(tokens[start:end]))

#tested
def compileReturn(tokens):
    if len(tokens) == 2:
        return(ReturnStatement([]))
    else:
        start = 1
        end = len(tokens)-1
        expression = compileExp(tokens[start:end], 0)
        return(ReturnStatement([expression]))

#tested
def compileExp(tokens, index):
    (startTerm, newIndex) = compileFirstTerm(tokens, index)
    if newIndex < len(tokens):
        opTerms = compileOpTerms(tokens, newIndex)
    else:
        opTerms = []
    return Expression(startTerm, opTerms)

#tested
def compileOpTerms(tokens, index):
    (opTerm, newIndex) = compileOpTerm(tokens, index)
    if newIndex < len(tokens):
        return [opTerm] + compileOpTerms(tokens, newIndex)
    else:
        return [opTerm]

#tested
def compileOpTerm(tokens, index):
    op = tokens[index]
    (term,newIndex) = compileFirstTerm(tokens,index+1)
    return((OpTerm(op, term), newIndex))

#tested
def compileFirstTerm(tokens, index):
    newIndex = 0
    #tested
    if type(tokens[index]) in [IntegerConstant,StringConstant,Keyword]:
        newIndex = index+1
        return((Term(tokens[index], []), newIndex))
    #tested
    elif tokens[index] in [Symbol('-'), Symbol('~')]:
        (term,newIndex) = compileFirstTerm(tokens,index+1)
        return((Term(UnaryOp(tokens[index]),term), newIndex))
    elif tokens[index] == Symbol('('):
        startExp = index+1
        endExp = findClosingBracket(tokens, index, '(', ')')
        exp = compileExp(tokens[startExp:endExp], 0)
        return((Term(exp, []), endExp))
    elif type(tokens[index]) == Identifier:
        #tested
        if len(tokens)-index == 1:
            newIndex = index+1
            return((Term(Name(tokens[index]), []), newIndex))
        else:
            #tested
            if tokens[index+1] == Symbol('['):
                startExp = index+2
                endExp = findClosingBracket(tokens,index+1,'[',']')
                exp = compileExp(tokens[startExp:endExp], 0)
                return((Term(Name(tokens[index]), [exp]), endExp+1))
            #tested
            elif tokens[index+1] == Symbol('('):
                startExp = index
                endExp = findClosingBracket(tokens,index+1,'(',')')+1
                subCall = compileSubroutineCall(tokens[startExp:endExp])
                return((Term(subCall, []), endExp+1))
            #tested
            elif tokens[index+1] == Symbol('.'):
                startExp = index+2
                endExp = findClosingBracket(tokens,index+1,'(',')')+1
                subCall = compileSubroutineCall(tokens[startExp:endExp])
                return((Term(subCall, []), endExp+1))
            #tested
            else:
                newIndex = index+1
                return((Term(Name(tokens[index]), []), newIndex))
    else:
        raise Exception(f"Error: {tokens[index]} is not a valid start of statement.")

#tested
def compileSubroutineCall(tokens):
    index = 0
    if len(tokens) > 1:
        if tokens[index+1] == Symbol('('):
            startList = index+2
            endList = findClosingBracket(tokens,index+1,'(',')')
            return(SubroutineCall(SubroutineName(tokens[index]), compileExpList(tokens[startList:endList+1], 0), []))
        elif tokens[index+1] == Symbol('.'):
            startList = index+4
            endList = findClosingBracket(tokens,index+3,'(',')')
            return(SubroutineCall(SubroutineName(tokens[index+2]), compileExpList(tokens[startList:endList+1], 0), [Name(tokens[index])]))
    raise Exception(f"Error: {tokens} is not a valid subroutine call.")

#tested
def compileExpList(tokens, index):
    exps = []
    if not (index > len(tokens)):
        (expsRaw, _) =findList(tokens,index,lambda x: x == Symbol(','),lambda x: x == Symbol(')'))
        exps = [compileExp(expRaw, 0) for expRaw in expsRaw]
        return (ExpressionList(exps))
    return(exps)

#tested
def compileVarDec(varDecRaw):
    jackType = compileType(varDecRaw[1])
    names = []
    for i in range(2, len(varDecRaw), 2):
        names.append(Name(varDecRaw[i]))
    return VarDec(jackType,names)

#returns the index of the first ;, throws exception if not found
#tested
def findEoS(tokens, i):
    end = -1
    for j in range(i, len(tokens)):
        if tokens[j] == Symbol(';'):
            end = j
            break
    if end == -1:
        raise Exception("Error: no end of statement found.")
    return end

#returns the index of the closing bracket of the first opening bracket
#tested
def findClosingBracket(tokens, start, startS, endS):
    startSymbol = Symbol(startS)
    endSymbol = Symbol(endS)
    brackets = 0
    foundFirstBracket = False
    i = start-1
    while (not (foundFirstBracket and brackets == 0) and i < len(tokens)-1):
        i += 1
        token = tokens[i]
        if token == startSymbol:
            brackets += 1
            foundFirstBracket = True
        elif token == endSymbol:
            brackets -= 1
    if not (i == start):
        return i
    else:
        raise Exception("Error: no closing bracket found")

#helper function used for cleaning xml output, exactly same as above but without converting input to symbols (I'm too lazy to go back and change the parameters for every time this is called)
def findClosingBracketPure(tokens, start, startS, endS):
    startSymbol = startS
    endSymbol = endS
    brackets = 0
    foundFirstBracket = False
    i = start-1
    while (not (foundFirstBracket and brackets == 0) and i < len(tokens)-1):
        i += 1
        token = tokens[i]
        if token == startSymbol:
            brackets += 1
            foundFirstBracket = True
        elif token == endSymbol:
            brackets -= 1
    if not (i == start):
        return i
    else:
        raise Exception("Error: no closing bracket found")



#tested
def i():
    return(open('input.txt', 'r').read())

def compileOut(tokens): 
    temp = open('temp.txt', 'w')
    temp.write(tokens)
    temp = open('temp.txt', 'r')
    lines = temp.readlines()
    cleanedLines = ""
    for line in lines:
        line = line.strip()
        if '<' not in line:
            continue
        elif line.count('<') == 1:
            endOfBrackets = findClosingBracketPure(line, 0, '<', '>')
        else:
            endOfFirstBracket = findClosingBracketPure(line, 0, '<', '>')
            endOfBrackets = findClosingBracketPure(line, endOfFirstBracket+3, '<', '>')
        cleanedLine = line[:endOfBrackets+1]
        cleanedLines += (cleanedLine) 
    #utilization of a py standard library xml formatter (just adds indentation, which is not theoretically necessary but much more readable)
    dom = xml.dom.minidom.parseString(cleanedLines) 
    xmlOut = dom.toprettyxml()
    out = open('out.xml', 'w')
    out.write(xmlOut)  


def main():
    rawInput = i()
    tokens = lex(rawInput)
    test = compileClass(tokens,0)
    #my compileClass function outputs a JackClass object, and all of my string representations of XMLable items includes ugly stuff like square bracketed lists
    #so I made another function that manually fixes line by line
    compileOut(str(test[0]))
    

main()