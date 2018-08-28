import os
import subprocess
import timeit
import argparse

OUT_FILE = 'out'
ERRORS_FILE = 'errors'

pltl_proccess = None
tableau_process = None


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--bfs-only', action='store_true')
    args.add_argument('--dfs-only', action='store_true')
    args.add_argument('--folder', default=None)
    args.add_argument('--timeit-amount', type=int, default=1)
    args.add_argument('--out-file')
    args.add_argument('--max-files', type=int)
    return args.parse_args()


def main():
    args = get_args()

    if os.path.isfile(OUT_FILE):
        os.remove(OUT_FILE)
    if os.path.isfile(ERRORS_FILE):
        os.remove(ERRORS_FILE)

    files = os.listdir(args.folder)
    files.sort()
    files = files[:args.max_files]

    for file_name in files:
        file_path = os.path.join(args.folder, file_name)

        def time_it_pltl():
            global pltl_proccess
            pltl_proccess = subprocess.Popen('./pltl/pltlGraphTree/pltl < {}'.format(file_path),
                                             universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                             shell=True)
            pltl_proccess.wait()

        def time_it_tableu_bfs():
            global tableau_process
            tableau_process = subprocess.Popen(bfs_cmd, universal_newlines=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE)
            tableau_process.wait()

        def time_it_tableu_dfs():
            global tableau_process
            cmd.append('--dfs-only')
            tableau_process = subprocess.Popen(dfs_cmd, universal_newlines=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE)
            tableau_process.wait()

        print('start pltl')
        pltl_time = timeit.timeit(time_it_pltl, number=args.timeit_amount)
        print('end pltl')

        pltl_output = pltl_proccess.stdout.readline()
        if pltl_output == 'satisfiable\n':
            expected_result = True
        elif pltl_output == 'unsatisfiable\n':
            expected_result = False
        else:
            assert False

        cmd = ['python', 'main.py', '--file', file_path, '--expected-result', str(expected_result),
               '--timeit']

        bfs_time = None
        dfs_time = None

        if not args.dfs_only:
            bfs_cmd = list(cmd)
            bfs_cmd.append('--bfs-only')
            print('start bfs tableau')
            bfs_time = timeit.timeit(time_it_tableu_bfs, number=args.timeit_amount)
            print('end bfs tableau')

        if not args.bfs_only:
            dfs_cmd = list(cmd)
            dfs_cmd.append('--dfs-only')
            print('start dfs tableau')
            dfs_time = timeit.timeit(time_it_tableu_dfs, number=args.timeit_amount)
            print('end dfs tableau')

        read_line = str(tableau_process.stdout.readlines())

        if tableau_process.returncode == 0:
            with open('{}.{}'.format(args.out_file, OUT_FILE), 'a') as out:
                out.write('{}\npltl time:{}\nbfs_tinme:{}\ndfs_time:{}\n\n'.format(file_path, pltl_time, bfs_time,
                                                                                   dfs_time))
        else:
            with open('{}.{}'.format(args.out_file, ERRORS_FILE), 'a') as out:
                out.write(file_path)
                out.write('\n')
                out.write(read_line)
                out.write('\n')
                out.write(str(tableau_process.stderr.readlines()))
                out.write('\n\n\n')


if __name__ == "__main__":
    main()
