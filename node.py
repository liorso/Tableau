import copy
from common import NodeType, Connective, TableauType
from formula import Formula


class Node:
    id = 0

    def __init__(self, tableau, parents, children, node_type, initial, formulas, node_id=None):
        if node_id:
            self.id = node_id
        else:
            Node.id += 1
            self.id = Node.id

        self.tableau = tableau
        self.parents = parents if type(parents) == set else {parents}
        self.children = children if type(children) == set else {children}
        self.node_type = node_type
        self.initial = initial
        self.formulas = set(copy.deepcopy(formulas))
        self.cloned = False
        self.find_successor_visited = False
        self.done_branch = False

        if node_type == NodeType.FUTURE:
            assert self.tableau.type == TableauType.DFS

        tableau.insert(self)

    def __repr__(self):
        return '\nid: {}, parents: {}, children: {}, node_type: {} initial: {}, formulas: {}, cloned: {}, ' \
               'done_branch: {}'.format(self.id, [node.id for node in self.parents],
                                        [node.id for node in self.children], self.node_type,
                                        self.initial, self.formulas, self.cloned, self.done_branch)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(id(self))

    def handle_alpha(self, formulas, node_has_children, formula_processed):
        new_formulas = copy.deepcopy(self.formulas)

        for formula in new_formulas:
            if formula == formula_processed:
                formula.mark()

        new_formulas.update(formulas)

        if self.tableau.type == TableauType.DFS and node_has_children:
            node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.FUTURE,
                         initial=self.initial, formulas=new_formulas)
        else:
            node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                         initial=self.initial, formulas=new_formulas)
        self.children.add(node1)

    def handle_beta(self, formulas, node_has_children, formula_processed):
        new_formulas = copy.deepcopy(self.formulas)

        # We want to first handle the shorter formula
        formulas = list(formulas)
        if len(formulas) > 1:
            formulas.sort()
            formula1, formula2 = formulas
        else:
            formula1, formula2 = formulas[0], None

        for formula in new_formulas:
            if formula == formula_processed:
                formula.mark()

        new_formulas.update({formula1})

        if self.tableau.type == TableauType.BFS:
            node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                         initial=self.initial, formulas=new_formulas)
        else:
            node_type = NodeType.FUTURE if node_has_children else NodeType.PRE_STATE

            node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=node_type,
                         initial=self.initial, formulas=new_formulas)

        self.children.add(node1)

        # we might have gotten only 1 formula, this can happen if both parts were identical
        if formula2:
            new_formulas = copy.deepcopy(self.formulas)

            for formula in new_formulas:
                if formula == formula_processed:
                    formula.mark()

            new_formulas.add(formula2)

            if self.tableau.type == TableauType.BFS:
                node2 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                             initial=self.initial, formulas=new_formulas)
            else:
                node2 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.FUTURE,
                             initial=self.initial, formulas=new_formulas)

            self.children.add(node2)

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

    def clear_find_successor_visited_flag(self, successors):
        self.find_successor_visited = False
        for successor in successors:
            successor.find_successor_visited = False

    def find_all_successors(self):
        successors = self.find_all_successors_rec()
        self.clear_find_successor_visited_flag(successors)
        return successors

    def find_all_successors_rec(self):
        if self.find_successor_visited:
            return set()

        self.find_successor_visited = True
        successors = {child for child in self.children if child.node_type != NodeType.REMOVED}

        for child in self.children:
            successors.update(child.find_all_successors_rec())

        return successors

    def simple_remove(self):
        for parent in self.parents:
            parent.children.remove(self)
        for child in self.children:
            child.parents.remove(self)
        self.node_type = NodeType.REMOVED

    def find_eventualities(self):
        eventualities = set([formula for formula in self.formulas if formula.is_eventuality()])
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
        successors = self.find_all_successors()
        ans = self.fulfilled_until_rec(first_formula, second_formula)
        self.clear_find_successor_visited_flag(successors)
        return ans

    def fulfilled_until_rec(self, first_formula, second_formula):
        if self.find_successor_visited:
            return False
        self.find_successor_visited = True
        first_formula_exists = False
        for formula in self.formulas:
            if second_formula == formula.formula_string:
                return True
            if first_formula == formula.formula_string:
                first_formula_exists = True

        if not first_formula_exists:
            return False
        for child in self.children:
            if child.fulfilled_until_rec(first_formula, second_formula):
                return True
        return False

    def fulfilled_not_globally(self, check_formula):
        successors = self.find_all_successors()
        successors.add(self)
        for successor in successors:
            fulfilled = False
            for formula in successor.formulas:
                if check_formula == formula.formula_string:
                    fulfilled = True
                    break
            if not fulfilled:
                return True
        return False

    def has_unfulfilled_eventuality(self):
        eventualities = self.find_eventualities()
        for eventuality in eventualities:
            symbol, index = eventuality.find_next_symbol(eventuality.formula_string)

            if symbol == Connective.FINALLY.value and not self.fulfilled_finally(eventuality.formula_string[2:-1]):
                return True
            if symbol == Connective.UNTIL.value and not self.fulfilled_until(eventuality.formula_string[1:index - 1],
                                                                             eventuality.formula_string[index + 2:-1]):
                return True
            if not self.fulfilled_not_globally(eventuality.formula_string[4:-2]):
                return True
        return False
