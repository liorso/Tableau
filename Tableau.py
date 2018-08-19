import math
import copy
from common import NodeType, TruthValue
from node import Node
from formula import Formula
# TODO ranks and initial in node creations


class Tableau:

    def __init__(self):
        self.root_nodes = {}
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}

        # TODO  - do we need?
        self.state_to_pre = []
        self.pre_to_state = []

    def __repr__(self):
        return f'root_nodes: {self.root_nodes}\npre_states: {self.pre_states}\n' \
               f'proto_states: {self.proto_states}\nstates: {self.states}'

    def insert(self, node):
        if node.node_type == NodeType.PRE_STATE:
            self.pre_states[node.id] = node
        if node.node_type == NodeType.STATE:
            self.states[node.id] = node
        if node.node_type == NodeType.PROTO:
            self.proto_states[node.id] = node

        if node.initial:
            self.root_nodes[node.id] = node

    def clone(self):
        for node in self.pre_states.values():
            if not node.cloned and len(node.children) == 0:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.PROTO, initial=False,
                                formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                node.children.add(new_node)

    def apply_alpha_beta(self):
        for node in self.proto_states.values():
            for formula in node.formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.STATE,
                                    initial=False, formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                    node.children.add(new_node)

                if not formula.marked and not formula.is_elementary():
                    formula.mark()

                    is_alpha, formulas = formula.is_alpha()
                    if is_alpha:
                        node.handle_alpha(formulas)

                    is_beta, formulas = formula.is_beta()
                    assert is_beta, 'formula must be alpha/beta/elementary'
                    node.handle_beta(formulas)

            if len(node.children) == 0:
                node.node_type = NodeType.STATE
                self.states[node.id] = node

        self.proto_states = {i: node for (i, node) in self.proto_states.items() if node.node_type == NodeType.PROTO}

    def remove_proto_states(self):
        for proto_state in self.proto_states.values():
            assert proto_state.node_type == NodeType.PROTO
            self.remove(proto_state)
        self.proto_states = {}

    def next_rule(self):
        for state in self.states.values():
            if not state.cloned:
                state.cloned = True
                if state.is_consistent():
                    next_formulas = state.get_next_formulas()
                    if len(next_formulas) == 0:
                        next_formulas = {Formula(TruthValue.TRUE)}

                    for pre_state in self.pre_states.values():
                        if next_formulas == pre_state.formulas:
                            pre_state.parents.add(state)
                            state.children.add(pre_state)
                            break

                    new_node = Node(tableau=self, parents=state, children=set(), node_type=NodeType.PRE_STATE,
                                    initial=False, formulas=next_formulas, rank=math.inf, min_child_rank=math.inf)
                    state.children.add(new_node)

    def __eq__(self, other):
        return self.root_nodes == other.root_nodes and self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states

    def remove_prestates(self):
        # if id == 1 (root) mark child as initial
        for pre_state in self.pre_states.values:
            assert pre_state.node_type == NodeType.PRE_STATE
            if pre_state.id == 1:
                for init_state in pre_state.childrens.value:
                    init_state.init = True
            self.remove(pre_state)
        self.pre_states = {}

    def remove_state(self, node):
        successors = node.find_all_successors()
        candidates = successors
        bad = successors
        bad = bad.add(node)
        for successor in successors:
            for parent in successor.parants:
                if parent not in bad:
                    candidates.remove(successor)
        candidates.add(node)
        for node_to_remove in candidates:
            node_to_remove.simple_remove()
            self.states.remove(node_to_remove)

    def remove_inconsistent(self):
        self.remove_non_successors()

    def remove_eventualities(self):
        for state in self.states:
            if state.has_unfulfilled_eventuality():
                self.remove_state(state)

    def remove_non_successors(self):
        done = False
        while not done:
            current_tableau = copy.deepcopy(self)
            for state in self.states:
                if len(state.children) == 0:
                    for parent in state.parents:
                        parent.children.remove(state)
                    state.node_type = NodeType.REMOVED
                    self.states.remove(state)
            if current_tableau == self:
                done = True


def construct_pretableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE, initial=True,
         formulas=[formula], rank=math.inf, min_child_rank=math.inf)

    while True:
        current_tableau = copy.deepcopy(tableau)
        tableau.clone()
        if current_tableau == tableau:
            break

        tableau.apply_alpha_beta()
        tableau.remove_proto_states()
        tableau.next_rule()

    return tableau


def build_tableau(formula):
    tableau = construct_pretableau(formula)
    tableau.remove_prestates()
    tableau.remove_inconsistent()

    while True:
        tableau.remove_eventualities()
        tableau.remove_non_successors()

    return tableau.is_open()


def main():
    build_tableau(Formula('X(p)'))


main()
