from sys import argv
from src.parser import parse_file
from src.typechecker import typecheck_program
from src.emitter import emit, CLI

def help():
    print("Expected args: python pylambda.py name_of_file.pylambda [--debug | --raw | --no-input]")

def main():
    if len(argv) < 2:
        help()
        exit()
    cli = CLI()
    if len(argv) > 2:
        cli.set_args(argv[2:])
    program = parse_file(argv[1])
    typed = typecheck_program(program)
    emit(typed, cli)

if __name__=="__main__":
    main()