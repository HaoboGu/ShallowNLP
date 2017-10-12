def count():
    filename = "ex2.tok"
    f = open(filename)
    line = f.readline()
    i = 0
    while line:
        words = line.split(" ")
        for item in words:
            if item:
                if item != '\n':
                    i += 1
                    print(item)
        line = f.readline()
    f.close()
    print(i)

count()