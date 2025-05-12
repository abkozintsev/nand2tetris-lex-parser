from parser import getParsed
from parseTypes import *

def getClassVars(jackClass):
    classVarTokens = jackClass.classVarDecs
    staticVars = {}
    fieldVars = {}
    i = 0
    j = 0
    for token in classVarTokens:
        names = token.varNames
        if token.staticOrField == Keyword("static"):
            for name in names:
                staticVars[name] = i
                i += 1
        else:
            for name in names:
                fieldVars[name] = j
                j += 1
    return (staticVars, fieldVars)
    
def main():
    jackClass = getParsed()
    (staticVars, fieldVars) = getClassVars(jackClass)
    print(staticVars)
    print(fieldVars)

main()