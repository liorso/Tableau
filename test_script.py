import os
import subprocess
import argparse

OUT_FILE = 'out'


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--bfs-only', action='store_true')
    args.add_argument('--dfs-only', action='store_true')
    args.add_argument('--folder', default=None)
    args.add_argument('--timeit-amount', type=int, default=1)
    args.add_argument('--out-file')
    args.add_argument('--max-files', type=int)
    args.add_argument('--skip-tableau', action='store_true')
    args.add_argument('--skip-pltl', action='store_true')
    args.add_argument('--verbose', action='store_true')
    return args.parse_args()


def main():
    args = get_args()

    out_file = '{}.{}'.format(args.out_file, OUT_FILE)
    if os.path.isfile(out_file):
        os.remove(out_file)

    files = os.listdir(args.folder)
    files.sort()
    files = files[:args.max_files]

    for file_name in files:
        file_path = os.path.join(args.folder, file_name)

        pltl_graph_time = 0
        pltl_tree_time = 0
        bfs_time = 0
        dfs_time = 0

        expected_result = None

        if not args.skip_pltl:
            pltl_graph_cmd = './pltl/pltlWolper/pltl graph verbose < {}'.format(file_path)
            pltl_tree_cmd = './pltl/pltlWolper/pltl tree verbose < {}'.format(file_path)

            for i in range(args.timeit_amount):
                if args.verbose:
                    print('start graph pltl')
                pltl_graph = subprocess.Popen(pltl_graph_cmd, universal_newlines=True, stderr=subprocess.PIPE,
                                              stdout=subprocess.PIPE, shell=True)
                pltl_graph.wait()
                if args.verbose:
                    print('finished graph pltl')

                output = pltl_graph.stdout.readlines()

                time_str = output[7][6:]
                time_str.replace('-', '+')
                pltl_graph_time += float(time_str)

                graph_result = output[6]
                if graph_result == 'Result: Formula is satisfiable.\n':
                    graph_result = 'true'
                elif graph_result == 'Result: Formula is not satisfiable.\n':
                    graph_result = 'false'
                else:
                    assert False, graph_result

                if args.verbose:
                    print('start tree pltl')
                pltl_tree = subprocess.Popen(pltl_tree_cmd, universal_newlines=True, stderr=subprocess.PIPE,
                                             stdout=subprocess.PIPE, shell=True)
                pltl_tree.wait()
                if args.verbose:
                    print('finished tree pltl')

                output = pltl_tree.stdout.readlines()

                pltl_tree_time += float(output[7][6:])

                tree_result = output[6]
                if tree_result == 'Result: Formula is satisfiable.\n':
                    tree_result = 'true'
                elif tree_result == 'Result: Formula is not satisfiable.\n':
                    tree_result = 'false'
                else:
                    assert False, graph_result

                assert tree_result == graph_result, 'tree_result: {}, graph_result:{}'.format(tree_result, graph_result)

        if not args.skip_tableau:
            cmd = ['python', 'main.py', '--file', file_path, '--timeit', '--timeit-amount', str(args.timeit_amount)]

            if expected_result:
                cmd.append(['--expected-result', expected_result])

            if not args.dfs_only:
                bfs_cmd = list(cmd)
                bfs_cmd.append('--bfs-only')

                if args.verbose:
                    print('start bfs tableau')
                bfs_process = subprocess.Popen(bfs_cmd, universal_newlines=True, stderr=subprocess.PIPE,
                                               stdout=subprocess.PIPE)
                bfs_process.wait()
                if args.verbose:
                    print('end bfs tableau')

                bfs_time = bfs_process.stdout.readlines()[0]

            if not args.bfs_only:
                dfs_cmd = list(cmd)
                dfs_cmd.append('--dfs-only')

                if args.verbose:
                    print('start dfs tableau')
                print(dfs_cmd)
                dfs_process = subprocess.Popen(dfs_cmd, universal_newlines=True, stderr=subprocess.PIPE,
                                               stdout=subprocess.PIPE)
                dfs_process.wait()
                if args.verbose:
                    print('end dfs tableau')

                dfs_time = dfs_process.stdout.readlines()[0]

        with open(out_file, 'a') as out:
            out.write('{}\npltl tree time:{}\npltl graph time:{} \nbfs_time:{}dfs_time:{}\n\n'
                      ''.format(file_path, pltl_tree_time, pltl_graph_time, bfs_time, dfs_time))


if __name__ == "__main__":
    main()
