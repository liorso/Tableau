from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula


def main():
    test_cases = [('!(!(a))', True),
                  ('(a)A(b)', True),
                  ('!((a)O(b))', True),
                  ('!(X(a))', True),
                  ('G(a)', True),
                  ('!((a)A(b))', True),
                  ('(a)O(b)', True),
                  ('(a)U(b)', True),
                  ('!((a)U(b))', True),
                  ('(!(a))A(!(X((a)U(b))))', True),
                  ('!(X(G(a)))', True),
                  ('(a)O(!(a))', True),
                  ('!((a)O(!(a)))', False),
                  ('(a)A(!(a))', False),
                  ('!((a)A(!(a)))', True),
                  ('((a)O(b))O(c)', True),
                  ('((a)A(!(a)))O((b)A(!(b)))', False),
                  ('((a)A(!(a)))O((a)A(!(a)))', False),
                  ('(((a)A(!(a)))O((a)A(!(a))))A(c)', False),
                  ('(((a)A(!(a)))O((a)A(!(a))))O(c)', True)
                  ]

    errors = []

    iterations = 10

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
