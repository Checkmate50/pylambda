from sys import argv
from src.parser import parse_file
from src.typechecker import typecheck_program

def help():
    print("Expected args: python pylambda.py name_of_file.pylambda [-v]")

def main():
    if len(argv) < 2:
        help()
        exit()
    program = parse_file(argv[1])
    typed = typecheck_program(program)
    print(typed)

if __name__=="__main__":
    main()