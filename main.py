from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula


def main():
    formulas_strings = ['!(!(a))', '(a)A(b)', '!((a)O(b))', '!(X(a))', 'G(a)', '!((a)A(b))', '(a)O(b)', '(a)U(b)',
                        '!((a)U(b))', '(!(a))A(!(X((a)U(b))))', '!(X(G(a)))', '(a)O(!(a))', '!((a)O(!(a)))',
                        '(a)A(!(a))', '!((a)A(!(a)))']
    expected_results = [True, True, True, True, True, True, True, True, True, True, True, True, False, False, True]

    bfs_to_dfs_errors = []
    result_to_expected_errors = []

    assert len(expected_results) == len(formulas_strings)

    for formula_string, expected_result in zip(formulas_strings, expected_results):
        print(f'checking formula {formula_string}')

        dfs_result = DfsTableau(Formula(formula_string), debug=False).build_tableau()
        bfs_result = BfsTableau(Formula(formula_string), debug=False).build_tableau()

        print(f'dfs_result: {dfs_result}, bfs_result {bfs_result}')

        if dfs_result != bfs_result:
            bfs_to_dfs_errors.append(formula_string)
        elif bfs_result != expected_result:
            result_to_expected_errors.append(formula_string)

    if len(bfs_to_dfs_errors) > 0:
        print(f'\nthe following formulas did not match between bfs and dfs:{bfs_to_dfs_errors}')
    if len(result_to_expected_errors) > 0:
        print(f'\nthe following formulas matched between bfs and dfs, but not to expected:{result_to_expected_errors}')
    if len(bfs_to_dfs_errors) == 0 and len(result_to_expected_errors) == 0:
        print('\nall formulas match')


if __name__ == "__main__":
    main()
