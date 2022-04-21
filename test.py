from tools.test_util import *
from sys import argv
import os

def help():
    print("Expected args: python test.py (name_of_file.pylambda | name_of_folder) [--err]")

def main():
    if len(argv) < 2:
        help()
        return
    if os.path.isdir(argv[1]):
        for (_, _, filenames) in os.walk(argv[1]):
            for filename in filenames:
                if not test_file(f"{argv[1]}/{filename}"):
                    print(f"Failure in file {filename}")
                    return
                print(f"{argv[1]}/{filename} run successfully")
        print(f"Tests run successfully on directory {argv[1]}")
        return
    if not test_file(argv[1]):
        print(f"Failure in file {argv[1]}")
    else:
        print(f"{argv[1]} run successfully")

if __name__=="__main__":
    main()