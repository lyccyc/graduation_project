test = [0,1,2,3,4]

for i in range(4):
    temp = test[i]
    test[i] = test[i + 1]
    test[i + 1] = temp

print(test)