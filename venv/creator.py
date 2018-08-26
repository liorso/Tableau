def mymain():
    s = '(a)O(a)'
    for i in range(1, 1000):
        s = '(' + s + ')O(a)'
    print(s)

mymain()
