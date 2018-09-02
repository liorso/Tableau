Run command:
'python main.py' - Command to run basic test cases. For specific formula tests please use flags.



Flags:
--single-test-case: gets one formula to test.
					example: 'python main.py --single-test-case "(a000)|(b000)"'

--bfs-only: doen't get anything. If on, only BFS is tested.

--dfs-only: doen't get anything. If on, only DFS is tested.

--bfs-debug: doen't get anything. If on, BFS logs are printed.

--dfs-debug: doen't get anything. If on, DFS logs are printed.

--file: gets a file path. Runs formula from the fle.
					example: 'python main.py --file "./formulas/c1/c1_a099.pltl"'
					
--timeit: doen't get anything. Prints the time took to run the test. First DFS result and then BFS.

--timeit-amount: gets number of iteration to run for time test.



Convantions:
* Connective:
	'&' - And
	'~' - Not
	'G' - Globally
	'X' - Next
	'F' - Finnaly
	'|' - Or
	'>' - Implies
	'U' - Until

	'1' - True
	'0' - False
	
* Litterals: The name should be exactly 4 characters, for example: 'a000'

* Brackets: Use only open bracket '(' and close ')'
			Each litteral and connective (except the main connective) should be serounded by brackets.
			Example: '((a000)|(b000))&(c000)'.