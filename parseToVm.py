from parser import *
from parseTypes import *

def getClassVars(jackClass : JackClass):
    classVarTokens = jackClass.classVarDecs
    classVars = {}
    i = 0
    j = 0
    for token in classVarTokens:
        names = token.varNames
        if token.staticOrField == Keyword("static"):
            for name in names:
                classVars[name] = ("static", i, token.jackType)
                i += 1
        else:
            for name in names:
                classVars[name] = ("field", j, token.jackType)
                j += 1
    return (classVars)

def getMethodVars(jackSubroutineDec : SubroutineDec):
    args = jackSubroutineDec.parameterList.parameters
    methodVars = {}
    i = 0
    for arg in args:
        name = arg[1]
        jackT = compileType(arg[0])
        methodVars[name] = ("arg", i, jackT)
    localDecs = jackSubroutineDec.subroutineBody.varDecs
    i = 0
    for localDec in localDecs:
        useful = localDec.value[1:-1]
        jackT = useful[0]
        namesSlice = useful[1:]
        names = []
        namesSlice = namesSlice[0]
        if type(namesSlice) == list:
            for i in range(0, len(namesSlice), 2):
                names.append(namesSlice[i])
        for name in names:
            methodVars[name] = ("local", i, jackT)
            i+=1
    return(methodVars)

def createSymbolTable(classVars, subroutine):
    methodVars = getMethodVars(subroutine)
    return(classVars | methodVars)

def main():
    jackClass = getParsed()
    classVars = getClassVars(jackClass)
    subroutines = jackClass.subroutineDecs
    for subroutine in subroutines:
        symbolTable = createSymbolTable(classVars, subroutine)
        print(symbolTable)


main()