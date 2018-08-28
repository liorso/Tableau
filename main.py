from dfs_tableau import DfsTableau
from bfs_tableau import BfsTableau
from formula import Formula
import argparse
import sys
import timeit
sys.setrecursionlimit(200000)


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--single-test-case', default=None)
    args.add_argument('--expected-result', default=None)
    args.add_argument('--bfs-only', action='store_true')
    args.add_argument('--dfs-only', action='store_true')
    args.add_argument('--bfs-debug', action='store_true')
    args.add_argument('--dfs-debug', action='store_true')
    args.add_argument('--iterations', type=int, default=1)
    args.add_argument('--file', default=None)
    args.add_argument('--timeit', action='store_true')
    args.add_argument('--timeit-amount', type=int, default=1)
    return args.parse_args()


def main():
    args = get_args()

    if args.expected_result in ['true', 'True', '1']:
        args.expected_result = True
    elif args.expected_result in ['false', 'False', '0']:
        args.expected_result = False
    else:
        assert args.expected_result is None, 'invalid expected result use true/false'

    formula_string = None

    if args.file:
        with open(args.file, 'r') as f:
            formula_string = f.readline()

    if args.single_test_case:
        formula_string = args.single_test_case

    if formula_string:
        if not args.bfs_only:
            if args.timeit:
                time = timeit.timeit(lambda: DfsTableau(Formula(formula_string), expected_result=args.expected_result,
                                                        debug=args.dfs_debug).build_tableau, number=args.timeit_amount)
                print(time)
            else:
                print('dfs:', DfsTableau(Formula(formula_string), expected_result=args.expected_result,
                                         debug=args.dfs_debug).build_tableau())

        if not args.dfs_only:
            if args.timeit:
                time = timeit.timeit(lambda: BfsTableau(Formula(formula_string), expected_result=args.expected_result,
                                                        debug=args.bfs_debug).build_tableau, number=args.timeit_amount)
                print(time)
            else:
                print('bfs:', BfsTableau(Formula(formula_string), expected_result=args.expected_result,
                                         debug=args.bfs_debug).build_tableau())

        return

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
                  ('(((((aaaa)|(~(bbbb)))&((bbbb)|(~(cccc))))&((cccc)|(~(aaaa))))&(~(aaaa)))&(aaaa)', False),
                  ('((a002)|(b002))&((G(c000))&(X(~(c000))))', False),
                  ('(((a001)|(b001))&((a002)|(b002)))&((G(c000))&(X(~(c000))))', False),
                  ('~((((a001)|(b001))&((a002)|(b002)))&((G(c000))&(X(~(c000)))))', True)
                  ]

    for i in range(args.iterations):
        for test_case in test_cases:
            formula_string, expected_result = test_case

            if not args.dfs_only:
                if args.timeit:
                    print(timeit.timeit(BfsTableau(Formula(formula_string), expected_result=expected_result,
                                                   debug=args.bfs_debug).build_tableau, number=args.timeit_amount))
                else:
                    BfsTableau(Formula(formula_string), expected_result=expected_result,
                               debug=args.bfs_debug).build_tableau()

            if not args.bfs_only:
                if args.timeit:
                    print(timeit.timeit(DfsTableau(Formula(formula_string), expected_result=expected_result,
                                                   debug=args.dfs_debug).build_tableau, number=args.timeit_amount))
                else:
                    DfsTableau(Formula(formula_string), expected_result=expected_result,
                               debug=args.dfs_debug).build_tableau()

    print('\nall formulas match, checked {} times'.format(args.iterations))


if __name__ == "__main__":
    main()
