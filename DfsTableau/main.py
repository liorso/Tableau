from DfsTableau.node import Node
from DfsTableau.formula import Formula
from DfsTableau.common import NodeType
from DfsTableau.Tableau import Tableau

def construct_next_branch(tableau):
    node = tableau.future_states.pop()
    node.node_type = NodeType.PRE_STATE
    tableau.pre_states[node.id] = node

    while True:
        if not tableau.clone():
            break
        tableau.apply_alpha_beta()
        tableau.remove_proto_states()
        tableau.next_rule()


def check_is_next_branch_valid(tableau):
    branch_root_node = tableau.get_next_branch()
    pass


def build_dfs_tableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=set(), children=set(), node_type=NodeType.FUTURE, initial=True,
         formulas=[formula])

    while len(tableau.future_states) > 0:
        construct_next_branch(tableau)
        print(tableau)
        exit(0)
        if check_is_next_branch_valid(tableau):
            return True

    return False

    tableau = construct_pretableau(formula)
    print('after construct_pretableau:')
    print(tableau)
    tableau.remove_prestates()
    print('\n\nafter remove_prestates:')
    print(tableau)
    tableau.remove_inconsistent()
    # print('\n\nafter remove_inconsistent:')
    # print(tableau)

    changed = True
    while changed:
        changed = tableau.remove_eventualities()
        changed = tableau.remove_non_successors() or changed

    print('\n\nfinal tableau:')
    print(tableau)
    return tableau.is_open()


def main():
    satisfiable = build_dfs_tableau(Formula('(a)O(b)'))
    if satisfiable:
        print('Satisfiable! :)')
    else:
        print('Not Satisfiable :(')


main()
