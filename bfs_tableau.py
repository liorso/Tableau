from node import Node
from common import NodeType, TableauType
from Tableau import Tableau


class BfsTableau:
    def __init__(self, formula, debug=False):
        self.tableau = Tableau(tableau_type=TableauType.BFS)
        self.formula = formula
        self.debug = debug

    def construct_pre_tableau(self):
        Node(tableau=self.tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE, initial=True,
             formulas=[self.formula])

        if self.debug:
            print('start loop:')
            print(self.tableau)

        while True:
            if not self.tableau.clone():
                # clone() didn't change the tableau, no need to continue
                break
            if self.debug:
                print('\nafter clone:')
                print(self.tableau)

            self.tableau.apply_alpha_beta()
            if self.debug:
                print('\nafter alpha beta')
                print(self.tableau)

            self.tableau.remove_proto_states()
            if self.debug:
                print('\nafter remove proto')
                print(self.tableau)

            self.tableau.next_rule()
            if self.debug:
                print('\nafter next')
                print(self.tableau)

    def build_tableau(self):
        self.construct_pre_tableau()
        if self.debug:
            print('after construct_pre_tableau:')
            print(self.tableau)

        self.tableau.remove_pre_states()
        if self.debug:
            print('\n\nafter remove_pre_states:')
            print(self.tableau)

        self.tableau.remove_inconsistent()
        if self.debug:
            print('\n\nafter remove_inconsistent:')
            print(self.tableau)

        changed = True
        while changed:
            changed = self.tableau.remove_eventualities()
            changed = self.tableau.remove_non_successors() or changed

        if self.debug:
            print('\n\nfinal tableau:')
            print(self.tableau)

        Node.id = 0
        return self.tableau.is_open()
