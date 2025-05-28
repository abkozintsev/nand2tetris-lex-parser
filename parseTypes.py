class XMLable():
    value = None
    def __str__(self):
        # lowerType = list(type(self).__name__)
        # lowerType[0] = lowerType[0].lower()
        # lowerType = ''.join(lowerType)
        # return(f"\n<{lowerType}> {self.value} \n</{lowerType}>")
        return(f"({self.value}, {type(self).__name__})")
    def __repr__(self):
        # lowerType = list(type(self).__name__)
        # lowerType[0] = lowerType[0].lower()
        # lowerType = ''.join(lowerType)
        # return(f"\n<{lowerType}> {self.value} \n</{lowerType}>")
        return(f"({self.value}, {type(self).__name__})")
    def __eq__(self, other):
        return(type(self) == type(other) and self.value == other.value)
    def __hash__(self):
        return hash(self.value)

class MonoToken(XMLable):
    def __str__(self):
        # return(str(self.value))
        return(f"({self.value}, {type(self).__name__})")
    def __repr__(self):
        # return(str(self.value))
        return(f"({self.value}, {type(self).__name__})")
    subtypes = None
    def __init__(self, value):
        if type(value) in self.subtypes:
            self.value = value
        else:
            raise Exception(f"Error: subtype of {type(self)} must be one of {self.subtypes}, instead it is {type(value)}.")
    def termVal(self):
        return(self.value.termVal())
        
class TerminalToken(MonoToken):
    # def __str__(self):
    #     lowerType = list(type(self).__name__)
    #     lowerType[0] = lowerType[0].lower()
    #     lowerType = ''.join(lowerType)
    #     return(f"\n<{lowerType}> {self.value} </{lowerType}>")
    # def __repr__(self):
    #     lowerType = list(type(self).__name__)
    #     lowerType[0] = lowerType[0].lower()
    #     lowerType = ''.join(lowerType)
    #     return(f"\n<{lowerType}> {self.value} </{lowerType}>")
    def termVal(self):
        return(self.value)

class Keyword(TerminalToken):
    subtypes = [str]

class Symbol(TerminalToken):
    subtypes = [str]

class IntegerConstant(TerminalToken):
    subtypes = [int]

class StringConstant(TerminalToken):
    subtypes = [str]

class Identifier(TerminalToken):
    subtypes = [str]

class JackClass(XMLable):
    def __init__(self, className, classVarDecs, subroutineDecs):
        self.value = [Keyword('class'),className,Symbol('{'),classVarDecs,subroutineDecs,Symbol('}')]
        self.className = className
        self.classVarDecs = classVarDecs
        self.subroutineDecs = subroutineDecs

class ClassVarDec(XMLable):
    def __init__(self, staticOrField, jackType, varNames):
        self.value = [staticOrField,jackType,varNames,Symbol(';')]
        if len(varNames) == 1:
            self.value[2] = varNames[0]
        elif len(varNames) > 1:
            temp = []
            for i in range(len(varNames)-1):
                temp.append(varNames[i])
                temp.append(Symbol(','))
            temp.append(varNames[-1])
            self.value[2]=temp
        self.staticOrField = staticOrField
        self.jackType = jackType
        self.varNames = varNames
        

class SubroutineDec(XMLable):
    def __init__(self, keyword, jackType, name, parameterList, subroutineBody):
        self.value = [keyword, jackType, name, Symbol('('), parameterList, Symbol(')'), subroutineBody]
        self.keyword = keyword
        self.jackType = jackType
        self.name = name
        self.parameterList = parameterList
        self.subroutineBody = subroutineBody

class ParameterList(XMLable):
    def __init__(self, parameters):
        temp = []
        if len(parameters) == 1:
            temp.append(parameters[0])
        elif len(parameters) > 1:
            for i in range(len(parameters)-1):
                temp.append(parameters[i][0])
                temp.append(parameters[i][1])
                temp.append(Symbol(','))
            temp.append(parameters[-1])
        self.value = temp
        self.parameters = parameters

class SubroutineBody(XMLable):
    def __init__(self, varDecs, statements):
        self.value = [Symbol('{'), varDecs, statements, Symbol('}')]
        self.varDecs = varDecs
        self.statements = statements

class VarDec(XMLable):
    def __init__(self, jackType, varNames):
        self.value = [Keyword('var'), jackType, varNames, Symbol(';')]
        if len(varNames) == 1:
            self.value[2] = varNames[0]
        elif len(varNames) > 1:
            temp = []
            for i in range(len(varNames)-1):
                temp.append(varNames[i])
                temp.append(Symbol(','))
            temp.append(varNames[-1])
            self.value[2]=temp
        self.jackType = jackType
        self.varNames = varNames
    
class Name(MonoToken):
    subtypes = [Identifier]
    

class JackType(MonoToken):
    subtypes = [Keyword, Name]

class SubroutineName(MonoToken):
    subtypes = [Identifier]


class Statements(MonoToken):
    subtypes = [list]
    def __len__(self):
        return len(self.value)
    def __str__(self):
        lowerType = list(type(self).__name__)
        lowerType[0] = lowerType[0].lower()
        lowerType = ''.join(lowerType)
        return(f"\n<{lowerType}> {self.value} \n</{lowerType}>")
    def __repr__(self):
        # print("repr call: ", self)
        lowerType = list(type(self).__name__)
        lowerType[0] = lowerType[0].lower()
        lowerType = ''.join(lowerType)
        return(f"\n<{lowerType}> {self.value} \n</{lowerType}>")

class LetStatement(XMLable):
    def __init__(self, name, expression1, expression2):
        self.value = [Keyword('let'), name]
        if len(expression1) == 1:
            self.value.append(Symbol('['))
            self.value.append(expression1)
            self.value.append(Symbol(']'))
        self.value.append(Symbol('='))
        self.value.append(expression2)
        self.value.append(Symbol(';'))
        self.expression1 = expression1
        self.name = name
        self.expression2 = expression2

class IfStatement(XMLable):
    def __init__(self, expression, statements1, statements2):
        self.value = [Keyword('if'), Symbol('('), expression, Symbol(')'), Symbol('{'), statements1,Symbol('}')]
        if len(statements2) > 0:
            self.value.append(Keyword('else'))
            self.value.append(Symbol('{'))
            self.value.append(statements2)
            self.value.append(Symbol('}'))
        self.expression = expression
        self.statements1 = statements1
        self.statements2 = statements2

class WhileStatement(XMLable):
    def __init__(self, expression, statements):
        self.value = [Keyword('while'), Symbol('('), expression, Symbol(')'), Symbol('{'), statements, Symbol('}')]
        self.expression = expression
        self.statements = statements

class DoStatement(XMLable):
    def __init__(self, subroutineCall):
        self.value = [Keyword('do'), subroutineCall, Symbol(';')]
        self.subroutineCall = subroutineCall

class ReturnStatement(XMLable):
    def __init__(self, expression):
        self.value = []
        self.value.append(Keyword('return'))
        if len(expression) == 1:
            self.value.append(expression[0])
        self.value.append(Symbol(';'))
        self.expression = expression

class Statement(MonoToken):
    subtypes = [LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement]

class OpTerm(XMLable):
    def __init__(self, op, term):
        self.value = (op, term)
        self.op = op
        self.term = term
    def __str__(self):
        return()

class Expression(XMLable):
    def __init__(self, startTerm, opTerms):
        self.value = [startTerm] + opTerms
        self.startTerm = startTerm
        self.opTerms = opTerms

class SubroutineCall(XMLable):
    def __init__(self, subName, expressionList, classOrName):
        if len(classOrName) == 1:
            self.value = [classOrName, Symbol('.'), subName, Symbol('('), expressionList, Symbol(')')]
        else:
            self.value = [subName, Symbol('('), expressionList, Symbol(')')]
        self.subName = subName
        self.expressionList = expressionList
        self.classOrName = classOrName

class ExpressionList(XMLable):
    def __init__(self,expressions):
        temp = []
        if len(expressions) == 1:
            temp.append(expressions[0])
        elif len(expressions) > 1:
            for i in range(len(expressions)-1):
                temp.append(expressions[i])
                temp.append(Symbol(','))
            temp.append(expressions[-1])
        self.value = temp

class Op(MonoToken):
    subtypes = [Symbol]

class UnaryOp(MonoToken):
    subtypes = [Symbol]

class KeywordConstant(MonoToken):
    subtypes = [Keyword]

class Term(XMLable):
    def __init__(self, x, y):
        #tested
        if type(x) in [IntegerConstant, StringConstant, Keyword, SubroutineCall]:
            self.value = x
        elif type(x) == Name:
            #tested
            if len(y) == 0:
                self.value = x
            #
            elif type(y[0]) == Expression:
                self.value = [x, Symbol('['), y, Symbol(']')]
        elif type(x) == Expression:
            self.value = [Symbol('('), x, Symbol(')')]
        #tested
        elif type(x) == UnaryOp:
            self.value = [x, y]
        self.x = x
        self.y = y
