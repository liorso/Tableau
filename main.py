from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula


def main():

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
                  ('(((a)&(~(a)))|((a)&(~(a))))|(c)', True),
                  ('(((a)|(~(b)))&((b)|(~(c))))&((c)|(~(a)))', True),
                  ('((a)|(~(b)))&((b)|(~(c)))', True),
                  ('((((a)|(~(b)))&((b)|(~(c))))&((c)|(~(a))))&(~(a))', True),
                  ('(((((a)|(~(b)))&((b)|(~(c))))&((c)|(~(a))))&(~(a)))&(a)', False)
                  ]

    errors = []

    iterations = 1

    for i in range(iterations):
        for test_case in test_cases:
            formula_string, expected_result = test_case

            dfs_result = DfsTableau(Formula(formula_string), debug=False).build_tableau()
            bfs_result = BfsTableau(Formula(formula_string), debug=False).build_tableau()

            if dfs_result != bfs_result or bfs_result != expected_result:
                errors.append(f'checked formula: {formula_string}, expected_result: {expected_result} '
                              f'bfs result: {bfs_result}, dfs result: {dfs_result}')

        if len(errors) > 0:
            print(f'\nafter {i} iterations got the following errors:')
            for error in errors:
                print(error)
            break

    if len(errors) == 0:
        print(f'\nall formulas match, checked {iterations} times')


if __name__ == "__main__":
    main()
