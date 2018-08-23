from BfsTableau.node import Node
from BfsTableau.formula import Formula
from BfsTableau.common import NodeType
from BfsTableau.Tableau import Tableau


def construct_pretableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE, initial=True, formulas=[formula])

    # print('start loop:')
    # print(tableau)
    i = 0
    while True:
        # input(f'start loop {i}')
        if not tableau.clone():
            # clone() didn't change the tableau, no need to continue
            break
        # print('\nafter clone:')
        # print(tableau)

        tableau.apply_alpha_beta()
        # print('\nafter alpha beta')
        # print(tableau)
        tableau.remove_proto_states()
        # print('\nafter remove proto')
        # print(tableau)

        tableau.next_rule()
        # print('\nafter next')
        # print(tableau)
        i += 1

    return tableau


def build_bfs_tableau(formula):
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
    satisfiable = build_bfs_tableau(Formula('((a)O(!(b)))A(((!(a))O(c))A(((!(a))O(!(c)))A(b)))'))
    if satisfiable:
        print('Satisfiable! :)')
    else:
        print('Not Satisfiable :(')


main()
