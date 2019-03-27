from seneca.engine.interpreter.code_modifier import CodeModifier
import ast

def test_code_modifier():
    with open('stubucks.py', 'r') as myfile:
        code=myfile.read()
    print("input code:")
    print(code)
    codeMod = CodeModifier('_sf')
    prefix = '_zxq_'
    code_out = codeMod.transform(code, prefix)
    print("output code:")
    print(code_out)
    if "@cleanup" in code_out:
        print("Success!")
    else:
        print("Test Failed!")


if __name__ == '__main__':
    test_code_modifier()
