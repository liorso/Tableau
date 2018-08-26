from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula


def main():

    test_cases = [('~(~(aaaa))', True),
                  ('(aaaa)&(bbbb)', True),
                  ('~((aaaa)|(bbbb))', True),
                  ('~(X(aaaa))', True),
                  ('G(aaaa)', True),
                  ('~((aaaa)&(bbbb))', True),
                  ('(aaaa)|(bbbb)', True),
                  ('(aaaa)U(bbbb)', True),
                  ('~((aaaa)U(bbbb))', True),
                  ('(~(aaaa))&(~(X((aaaa)U(bbbb))))', True),
                  ('~(X(G(aaaa)))', True),
                  ('(aaaa)|(~(aaaa))', True),
                  ('~((aaaa)|(~(aaaa)))', False),
                  ('(aaaa)&(~(aaaa))', False),
                  ('~((aaaa)&(~(aaaa)))', True),
                  ('((aaaa)|(bbbb))|(cccc)', True),
                  ('((aaaa)&(~(aaaa)))|((bbbb)&(~(bbbb)))', False),
                  ('((aaaa)&(~(aaaa)))|((aaaa)&(~(aaaa)))', False),
                  ('(((aaaa)&(~(aaaa)))|((aaaa)&(~(aaaa))))&(cccc)', False),
                  ('(((aaaa)&(~(aaaa)))|((aaaa)&(~(aaaa))))|(cccc)', True),
                  ('(((aaaa)&(~(aaaa)))|((aaaa)&(~(aaaa))))|(cccc)', True),
                  ('(((aaaa)|(~(bbbb)))&((bbbb)|(~(cccc))))&((cccc)|(~(aaaa)))', True),
                  ('((aaaa)|(~(bbbb)))&((bbbb)|(~(cccc)))', True),
                  ('((((aaaa)|(~(bbbb)))&((bbbb)|(~(cccc))))&((cccc)|(~(aaaa))))&(~(aaaa))', True),
                  ('(((((aaaa)|(~(bbbb)))&((bbbb)|(~(cccc))))&((cccc)|(~(aaaa))))&(~(aaaa)))&(aaaa)', False)
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
