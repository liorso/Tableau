import copy
import math
from common import NodeType, Connective


class Node:
    id = 0

    def __init__(self, tableau, parents, children, node_type, initial, formulas, rank, min_child_rank):
        Node.id += 1
        self.id = Node.id
        self.tableau = tableau
        self.parents = parents if type(parents) == set else {parents}
        self.children = children if type(children) == set else set( [children])
        self.node_type = node_type
        self.initial = initial
        self.formulas = set(copy.deepcopy(formulas))
        self.rank = rank
        self.min_child_rank = min_child_rank
        self.cloned = False

        tableau.insert(self)

    def __repr__(self):
        return f'id: {self.id}, parents: {self.parents}, children: {self.children}, node_type: {self.node_type}' \
               f'initial: {self.initial}, formulas: {self.formulas}, rank: {self.rank}, ' \
               f'min_child_rank: {self.min_child_rank}'

    def __eq__(self, other):
        return self.id == other.id

    def handle_alpha(self, formulas):
        node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=self.formulas.update(formulas),
                     rank=math.inf, min_child_rank=math.inf)

        self.children.append(node1)

    def handle_beta(self, formulas):
        node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=self.formulas.update(formulas[0]),
                     rank=math.inf, min_child_rank=math.inf)

        node2 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=self.formulas.update(formulas[1]),
                     rank=math.inf, min_child_rank=math.inf)

        self.children.append(node1)
        self.children.append(node2)

    def is_consistent(self):
        for formula in self.formulas:
            if formula.formula_string[0] == Connective.NOT.value:
                for second_formula in self.formulas:
                    if formula.formula_string[2:-1] == second_formula.formula_string:
                        return False
        return True

    def get_next_formulas(self):
        return {formula[2:-1] for formula in self.formulas if formula.is_next()}
