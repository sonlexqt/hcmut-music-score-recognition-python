import math

value = 41

for i in range(20, 60):
    if math.isclose(value, i, rel_tol=0.1):
        print('+ i:', i)
    else:
        print('i:', i)
