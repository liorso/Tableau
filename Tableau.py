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
        return f'pre_states: {self.pre_states}\n' \
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
        changed = False
        for node in self.pre_states.values():
            if not node.cloned and len(node.children) == 0:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.PROTO, initial=False,
                                formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                node.children.add(new_node)
                changed = True
        return changed

    def apply_alpha_beta(self):
        for node in self.proto_states.values():
            for formula in node.formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.STATE,
                                    initial=False, formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                    node.children.add(new_node)

                elif not formula.marked and not formula.is_elementary():
                    formula.mark()

                    is_alpha, formulas = formula.is_alpha()
                    formulas = {Formula(formulas[0]), Formula(formulas[1])}
                    if is_alpha:
                        node.handle_alpha(formulas)

                    else:
                        is_beta, formulas = formula.is_beta()
                        formulas = {Formula(formulas[0]), Formula(formulas[1])}
                        assert is_beta, 'formula must be alpha/beta/elementary'
                        node.handle_beta(formulas)

            if len(node.children) == 0:
                node.node_type = NodeType.STATE
                self.states[node.id] = node

        self.proto_states = {i: node for (i, node) in self.proto_states.items() if node.node_type == NodeType.PROTO}

    def remove_proto_states(self):
        for proto_state in self.proto_states.values():
            assert proto_state.node_type == NodeType.PROTO
            proto_state.remove()
        self.proto_states = {}

    def next_rule(self):
        for state in self.states.values():
            if not state.cloned:
                state.cloned = True
                if state.is_consistent():
                    next_formulas = state.get_next_formulas()
                    if len(next_formulas) == 0:
                        next_formulas = {Formula(TruthValue.TRUE.value)}

                    found_pre_state = False
                    for pre_state in self.pre_states.values():
                        if next_formulas == pre_state.formulas:
                            pre_state.parents.add(state)
                            state.children.add(pre_state)
                            found_pre_state = True
                            continue

                    if not found_pre_state:
                        new_node = Node(tableau=self, parents=state, children=set(), node_type=NodeType.PRE_STATE,
                                    initial=False, formulas=next_formulas, rank=math.inf, min_child_rank=math.inf)
                        state.children.add(new_node)

    def __eq__(self, other):
        return self.root_nodes == other.root_nodes and self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states

    def remove_prestates(self):
        # if id == 1 (root) mark child as initial
        for pre_state in self.pre_states.values():
            assert pre_state.node_type == NodeType.PRE_STATE
            if pre_state.id == 1:
                for init_state in pre_state.children:
                    init_state.init = True
            pre_state.remove()
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
        removed = False
        for state in self.states.values():
            if state.has_unfulfilled_eventuality():
                self.remove_state(state)
                removed = True
        return removed

    #TODO: Daniel, please check the logic still the same
    #1. remove is now bool
    #2. last line change to node.node_type != NodeType.REMOVED and not ==
    def remove_non_successors(self):
        changed = False
        removed = True
        while removed:
            removed = False
            for state in self.states.values():
                print(len(state.children), state)
                if len(state.children) == 0 and state.node_type != NodeType.REMOVED:
                    for parent in state.parents:
                        parent.children.remove(state)
                    state.node_type = NodeType.REMOVED
                    removed = True
                    changed = True
        self.states = {node_id: node for node_id, node in self.states.items() if node.node_type != NodeType.REMOVED}
        return changed


def construct_pretableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE, initial=True,
         formulas=[formula], rank=math.inf, min_child_rank=math.inf)

    #print('start loop:')
    #print(tableau)
    i = 0
    while True:
        #input(f'start loop {i}')
        if not tableau.clone():
            # clone() didn't change the tableau, no need to continue
            break
        #print('\nafter clone:')
        #print(tableau)

        tableau.apply_alpha_beta()
        #print('\nafter alpha beta')
        #print(tableau)
        tableau.remove_proto_states()
        #print('\nafter remove proto')
        #print(tableau)
        if i == 2:
            import pdb
            #pdb.set_trace()
        tableau.next_rule()
        #print('\nafter next')
        #print(tableau)
        i += 1

    return tableau


def build_tableau(formula):
    tableau = construct_pretableau(formula)
    print('after construct_pretableau:')
    print(tableau)
    tableau.remove_prestates() #TODO: bug with init flag
    print('\n\nafter remove_prestates:')
    print(tableau)
    tableau.remove_inconsistent()
    print('\n\nafter remove_inconsistent:')
    print(tableau)

    changed = True
    while changed:
        changed = tableau.remove_eventualities()
        changed = tableau.remove_non_successors() or changed

    # return tableau.is_open()


def main():
    build_tableau(Formula('F(!(!(((a)A(c))O((b)A(!(b))))))'))


main()
