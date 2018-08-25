from node import Node
from common import NodeType
from Tableau import Tableau


class DfsTableau:
    def __init__(self, formula, debug=False):
        self.tableau = Tableau()
        self.formula = formula
        self.debug = debug

    def construct_next_branch(self):
        node = self.tableau.future_states.pop()
        node.node_type = NodeType.PRE_STATE
        self.tableau.pre_states[node.id] = node

        while True:
            if not self.tableau.clone():
                break
            self.tableau.apply_alpha_beta()
            self.tableau.remove_proto_states()
            self.tableau.next_rule()

    def check_is_next_branch_valid(self):
        branch_tableau = self.tableau.get_next_branch()

        if self.debug:
            print('\nbranch_tableau')
            print(branch_tableau)

        branch_tableau.remove_pre_states()
        if self.debug:
            print('\nafter remove pre_states')
            print(branch_tableau)

        branch_tableau.remove_inconsistent()
        if self.debug:
            print('\n\nafter remove_inconsistent:')
            print(branch_tableau)

        changed = True
        while changed:
            changed = branch_tableau.remove_eventualities()
            changed = branch_tableau.remove_non_successors() or changed

        if self.debug:
            print('\n\nfinal tableau:')
            print(branch_tableau)

        return branch_tableau.is_open()

    def build_tableau(self):
        Node(tableau=self.tableau, parents=set(), children=set(), node_type=NodeType.FUTURE, initial=True,
             formulas=[self.formula])

        while len(self.tableau.future_states) > 0:
            self.construct_next_branch()

            if self.debug:
                print('next branch\n')
                print(self.tableau)

            if self.check_is_next_branch_valid():
                Node.id = 0
                return True
        Node.id = 0
        return False
