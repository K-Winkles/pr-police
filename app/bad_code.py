import os

def do_thing(x, x2, x2_):
    result = 0
    for i in range(len(x)):
        result = result + x[i]
    result2 = result / len(x)
    result3 = result2 * x2
    result4 = result3 + x2_
    return result4

data = [1,2,3,4,5]
print(do_thing(data, 100, do_thing(data, 100, do_thing(data, 100, 0))))
