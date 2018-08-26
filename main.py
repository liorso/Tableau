from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula
import timeit

def m():
    print('a')

def main():
    formula_string_ = '((G((~(a))|(~(b))))&((G(F(a)))&(G(F(b)))))&((G((a)>(X(a))))&(G((b)>(X(b)))))'

    print('BFS:', BfsTableau(Formula(formula_string_), debug=False).build_tableau())
    # print('DFS:', DfsTableau(Formula(formula_string_), debug=False).build_tableau())
    # # print('DFS:', timeit.timeit(DfsTableau(Formula(formula_string_), debug=False).build_tableau, number=1))
    # # print('BFS:', timeit.timeit(BfsTableau(Formula(formula_string_), debug=False).build_tableau, number=1))
    # return

    test_cases = [('~(~(a))', True),
                  ('(a)&(b)', True),
                  ('~((a)|(b))', True),
                  ('~(X(a))', True),
                  ('G(a)', True),
                  ('~((a)&(b))', True),
                  ('(a)|(b)', True),
                  ('(a)U(b)', True),
                  ('~((a)U(b))', True),
                  ('(~(a))&(~(X((a)U(b))))', True),
                  ('~(X(G(a)))', True),
                  ('(a)|(~(a))', True),
                  ('~((a)|(~(a)))', False),
                  ('(a)&(~(a))', False),
                  ('~((a)&(~(a)))', True),
                  ('((a)|(b))|(c)', True),
                  ('((a)&(~(a)))|((b)&(~(b)))', False),
                  ('((a)&(~(a)))|((a)&(~(a)))', False),
                  ('(((a)&(~(a)))|((a)&(~(a))))&(c)', False),
                  ('(((a)&(~(a)))|((a)&(~(a))))|(c)', True),
                  #('(((a)&(~(a)))|((a)&(~(a))))|(c)', True),
                  # ('(((a)|(~(b)))&((b)|(~(c))))&((c)|(~(a)))', True),
                  #('((a)|(~(b)))&((b)|(~(c)))', True),  # TODO - fails in DFS
                  #('((((a)|(~(b)))&((b)|(~(c))))&((c)|(~(a))))&(~(a))', True)  # TODO - fails
                  ]

    errors = []

    iterations = 10

    for i in range(iterations):
        for test_case in test_cases:
            formula_string, expected_result = test_case

            #dfs_result = DfsTableau(Formula(formula_string), debug=False).build_tableau()
            bfs_result = BfsTableau(Formula(formula_string), debug=False).build_tableau()

            # if dfs_result != bfs_result or bfs_result != expected_result:
            #   errors.append(f'checked formula: {formula_string}, expected_result: {expected_result} '
            #                   f'bfs result: {bfs_result}, dfs result: {dfs_result}')
            if bfs_result != expected_result:
               errors.append(f'checked formula: {formula_string}, expected_result: {expected_result} '
                             f'bfs result: {bfs_result}')

        if len(errors) > 0:
            print(f'\nafter {i} iterations got the following errors:')
            for error in errors:
                print(error)
            break

    if len(errors) == 0:
        print(f'\nall formulas match, checked {iterations} times')


if __name__ == "__main__":
    main()

def mymain():
    s = '(a)O(a)'
    for i in range(1, 1000):
        s = '(' + s + ')A(a)'
    print(s)

mymain()