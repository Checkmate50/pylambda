from sys import argv
from src.parser import parse_file

def help():
    print("Expected args: python pylambda.py name_of_file.pylambda [-v]")

def main():
    if len(argv) < 2:
        help()
        exit()
    print(parse_file(argv[1]))

if __name__=="__main__":
    main()