import copy
import math
from common import NodeType, Connective
from formula import Formula


class Node:
    id = 0

    def __init__(self, tableau, parents, children, node_type, initial, formulas, rank, min_child_rank):
        Node.id += 1
        self.id = Node.id
        self.tableau = tableau
        self.parents = parents if type(parents) == set else {parents}
        self.children = children if type(children) == set else {children}
        self.node_type = node_type
        self.initial = initial
        self.formulas = set(copy.deepcopy(formulas))
        self.rank = rank
        self.min_child_rank = min_child_rank
        self.cloned = False
        self.loop = False

        tableau.insert(self)

    def __repr__(self):
        return f'id: {self.id}, parents: {[node.id for node in self.parents]}, ' \
               f'children: {[node.id for node in self.children]}, node_type: {self.node_type} ' \
               f'initial: {self.initial}, formulas: {self.formulas}, rank: {self.rank}, ' \
               f'min_child_rank: {self.min_child_rank}, cloned: {self.cloned}'

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(id(self))

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
        return {Formula(formula.formula_string[2:-1]) for formula in self.formulas if formula.is_next()}

    def remove(self):
        for parent in self.parents:
            parent.children.remove(self)
            parent.children.update(self.children)

        for child in self.children:
            child.parents.remove(self)
            child.parents.update(self.parents)

    def find_all_successors(self):
        successors = self.children
        for successor in successors:
            successors.update(successor.children)
        return successors

    def simple_remove(self):
        for parent in self.parents:
            parent.children.remove(self)
        for child in self.children:
            child.parents.remove(self)
        self.node_type = NodeType.REMOVED

    def find_eventualities(self):
        eventualities = set([])
        for formula in self.formulas:
            if formula.is_eventuality():
                eventualities.add(formula)
        return eventualities

    def fulfilled_finally(self, check_formula):
        successors = self.find_all_successors()
        successors.add(self)
        for successor in successors:
            for formula in successor.formulas:
                if check_formula == formula.formula_string:
                    return True
        return False

    def fulfilled_until(self, first_formula, second_formula):
        if self.loop:
            return False
        self.loop = True
        first_formula_exists = False
        for formula in self.formulas:
            if second_formula == formula.formula_string:
                return True
            if first_formula == formula.formula_string:
                first_formula_exists = True
        if not first_formula_exists:
            return False
        for child in self.children:
            if child.fulfilled_until(first_formula, second_formula):
                return True
        return False

    def fulfilled_not_globally(self, check_formula):
        successors = self.find_all_successors()
        successors.add(self)
        for successor in successors:
            fulfilled = False
            for formula in successor.formulas:
                if check_formula == formula:
                    fulfilled = True
                    break
            if not fulfilled:
                return True
        return False

    def has_unfulfilled_eventuality(self):
        eventualities = self.find_eventualities()
        for eventuality in eventualities:
            symbol, index = Formula._find_next_symbol(eventuality.formula_string)
            if symbol == Connective.FINALLY.value and not self.fulfilled_finally(eventuality.formula_string[2:-1]):
                return True
            if symbol == Connective.UNTIL.value and not self.fulfilled_until(eventuality.formula_string[1:index - 1],\
                                                                             eventuality.formula_string[index + 2:-1]):
                return True
            # TODO: better way to prevent loops?
            successors = self.find_all_successors()
            successors.add(self)
            for successor in successors:
                successor.loop = False
            if not self.fulfilled_not_globally(eventuality.formula_string[4:-2]):
                return True
        return False
