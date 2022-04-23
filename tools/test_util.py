import subprocess
from typing import Optional, List

def interpret_file(command : str, filename : str) -> Optional[str]:
    interp = subprocess.Popen(["python", f"{command}.py", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    interp_out = subprocess.Popen(["python", "-"], stdin=interp.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res1 = interp.stderr.read()
    if res1 != b"":
        print(res1.decode("UTF-8"))
        return None
    interp.stdout.close()
    res2 = interp_out.communicate()
    if res2[1] != b"":
        print(res2[1].decode("UTF-8"))
        return None
    return res2[0].decode("UTF-8")

def clean(result : str) -> List[str]:
    return [x.strip() for x in result.split("\n")]

def compare(result1 : str, result2 : str) -> bool:
    data1 = clean(result1)
    data2 = clean(result2)
    ln = 1
    for line1, line2 in zip(data1, data2):
        if line1 != line2:
            print (f"Unexpected result on line {ln}: expected {line2}, got {line1}")
            return False
        ln += 1
    return True

def test_file(filename : str) -> bool:
    result1 = interpret_file("pylambda", filename)
    if result1 is None:
        return False
    result2 = interpret_file("tools/pylambda_to_python", filename)
    if result2 is None:
        return False
    return compare(result1, result2)