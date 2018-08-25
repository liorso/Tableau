from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula


def main():
    formulas_strings = ['!(!(a))', '(a)A(b)', '!((a)O(b))', '!(X(a))', 'G(a)', '!((a)A(b))', '(a)O(b)', '(a)U(b)',
                        '!((a)U(b))', '(!(a))A(!(X((a)U(b))))', '!(X(G(a)))', '(a)O(!(a))', '!((a)O(!(a)))',
                        '(a)A(!(a))', '!((a)A(!(a)))', '((a)O(b))O(c)', '((a)A(!(a)))O((b)A(!(b)))',
                        '((a)A(!(a)))O((a)A(!(a)))']
    expected_results = [True, True, True, True, True, True, True, True, True, True, True, True, False, False, True,
                        True, False, False]

    errors = []

    assert len(expected_results) == len(formulas_strings)
    iterations = 10

    for i in range(iterations):
        for formula_string, expected_result in zip(formulas_strings, expected_results):

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
