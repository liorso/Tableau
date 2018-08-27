import os


def make_globally_pattern():
    os.mkdir('globally')
    s = '(G(a000))&(G(a001))'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({s})&(G({new_node_name}))'

        f = open(f'globally/globally_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def make_finally_pattern():
    os.mkdir('finally')
    s = '(F(a000))&(F(a001))'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({s})&(F({new_node_name}))'

        f = open(f'finally/finally_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def make_or_pattern():
    os.mkdir('or')
    for i in range(1, 21):
        s = '(aaaa)|(aaaa)'
        for j in range(0, 100*i):
            s = '(' + s + ')|(aaaa)'
        f = open(f'or/or_{i}.pltl', 'w+')
        f.write(s)
        f.close()


def make_until1_pattern():
    os.mkdir('until1')
    s = '(a000)U(a001)'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({s})U({new_node_name})'

        f = open(f'until1/until1_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def make_until2_pattern():
    os.mkdir('until2')
    s = '(a000)U(a001)'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({new_node_name})U({s})'

        f = open(f'until2/until2_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def make_c1_pattern():
    os.mkdir('c1')
    s = '(G(F(a000)))|(G(F(a001)))'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({s})|(G(F({new_node_name})))'

        f = open(f'c1/c1_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def make_c2_pattern():
    os.mkdir('c2')
    s = '(G(F(a000)))&(G(F(a001)))'
    for i in range(2, 100):
        new_node_name = f'a00{i}' if i < 10 else f'a0{i}'
        s = f'({s})&(G(F({new_node_name})))'

        f = open(f'c2/c2_{new_node_name}.pltl', 'w+')
        f.write(s)
        f.close()


def main():
    make_globally_pattern()
    make_finally_pattern()
    make_or_pattern()
    make_until1_pattern()
    make_until2_pattern()
    make_c1_pattern()
    make_c2_pattern()


main()
