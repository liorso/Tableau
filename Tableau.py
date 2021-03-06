from common import NodeType, TruthValue, TableauType
from node import Node
from formula import Formula


class Tableau:

    def __init__(self, tableau_type):
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}
        self.future_states = []  # We use list as a stack cause we care about order
        self.type = tableau_type

    def __repr__(self):
        return 'pre_states: {}\nproto_states: {}\n future_states: {}\nstates: {}' \
               ''.format(self.pre_states, self.proto_states, self.future_states, self.states)

    def insert(self, node):
        if node.node_type == NodeType.PRE_STATE:
            self.pre_states[node.id] = node
        elif node.node_type == NodeType.STATE:
            self.states[node.id] = node
        elif node.node_type == NodeType.PROTO:
            self.proto_states[node.id] = node
        elif node.node_type == NodeType.FUTURE:
            assert self.type == TableauType.DFS
            self.future_states.append(node)

    def clone(self):
        changed = False
        for node in self.pre_states.values():
            if not node.cloned and len(node.children) == 0:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.PROTO,
                                initial=node.initial, formulas=node.formulas)
                node.children.add(new_node)
                changed = True
        return changed

    def apply_alpha_beta(self):
        for node in self.proto_states.values():
            node_has_children = False

            formulas = list(node.formulas)
            formulas.sort()
            
            for formula in formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.STATE,
                                    initial=node.initial, formulas=node.formulas)
                    node.children.add(new_node)

                elif not formula.marked and not formula.is_elementary():

                    is_alpha, formulas = formula.is_alpha()
                    formulas = {Formula(formulas[0]), Formula(formulas[1])}
                    if is_alpha:
                        node.handle_alpha(formulas, node_has_children, formula)
                        node_has_children = True

                    else:
                        is_beta, formulas = formula.is_beta()
                        formulas = {Formula(formulas[0]), Formula(formulas[1])}
                        assert is_beta, 'formula must be alpha/beta/elementary'
                        node.handle_beta(formulas, node_has_children, formula)
                        node_has_children = True

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
                            break

                    if not found_pre_state:
                        new_node = Node(tableau=self, parents=state, children=set(), node_type=NodeType.PRE_STATE,
                                        initial=False, formulas=next_formulas)
                        state.children.add(new_node)

    def __eq__(self, other):
        return self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states

    def remove_pre_states(self):
        for pre_state in self.pre_states.values():
            assert pre_state.node_type == NodeType.PRE_STATE
            pre_state.remove()
        self.pre_states = {}

    @staticmethod
    def remove_state(node):
        successors = node.find_all_successors()
        candidates = set(successors)
        bad = set(successors)
        bad.add(node)

        changed = True
        while changed:
            changed = False
            for successor in successors:
                for parent in successor.parents:
                    if parent not in bad:
                        changed = True
                        candidates.remove(successor)
                        bad.remove(successor)
                        break

            successors = set(candidates)

        candidates.add(node)
        for node_to_remove in candidates:
            node_to_remove.simple_remove()
        return candidates

    @staticmethod
    def find_child_to_handle(children):
        for child in children:
            if child.node_type == NodeType.PRE_STATE and not child.done_branch:
                return child
        assert False, 'child not found'

    def remove_inconsistent(self):
        self.remove_non_successors()

    def remove_eventualities(self):
        removed = False
        changed_in_last_round = True

        while changed_in_last_round:
            changed_in_last_round = False
            for state in self.states.values():
                if state.node_type != NodeType.REMOVED and state.has_unfulfilled_eventuality():
                    self.remove_state(state)
                    removed = True
                    changed_in_last_round = True
        self.states = {node_id: node for node_id, node in self.states.items() if node.node_type != NodeType.REMOVED}
        return removed

    def remove_non_successors(self):
        changed = False
        removed = True
        while removed:
            removed = False
            for state in self.states.values():
                if len(state.children) == 0 and state.node_type != NodeType.REMOVED:
                    for parent in state.parents:
                        parent.children.remove(state)
                    state.node_type = NodeType.REMOVED
                    removed = True
                    changed = True
        self.states = {node_id: node for node_id, node in self.states.items() if node.node_type != NodeType.REMOVED}
        return changed

    def is_child_in_tableau(self, child):
        # return child if exists, else None
        if child.node_type == NodeType.PRE_STATE:
            return self.pre_states.get(child.id, None)
        if child.node_type == NodeType.STATE:
            return self.states.get(child.id, None)
        assert False, "Not good?"

    def get_next_branch(self):
        branch, leaf = self._build_next_branch()
        self._mark_branch_as_done(leaf)
        return branch

    def _get_original_node(self, node):
        if node.node_type == NodeType.PRE_STATE:
            return self.pre_states[node.id]
        elif node.node_type == NodeType.STATE:
            return self.states[node.id]
        assert False

    def _mark_branch_as_done(self, leaf):
        curr_leaf = leaf
        original_node = self._get_original_node(curr_leaf)
        original_node.done_branch = True
        curr_leaf.done_branch = True
        (curr_leaf,) = curr_leaf.parents

        while len(curr_leaf.parents) > 0:
            if curr_leaf == leaf:
                return

            original_node = self._get_original_node(curr_leaf)

            for child in original_node.children:
                if not child.done_branch:
                    return
            original_node.done_branch = True
            curr_leaf.done_branch = True

            if len(curr_leaf.parents) == 1:
                (curr_leaf, ) = curr_leaf.parents

            else:
                (parent1, parent2) = curr_leaf.parents
                curr_leaf = parent2 if parent1.done_branch else parent1

    def _build_next_branch(self):
        assert self.type == TableauType.DFS
        new_tableau = Tableau(tableau_type=TableauType.DFS)

        original_root = self.pre_states[1]
        original_curr_root = original_root
        new_curr_root = Node(tableau=new_tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE,
                             initial=True, formulas=original_root.formulas, node_id=original_root.id)

        while True:
            if len(original_curr_root.children) == 0:
                return new_tableau, new_curr_root

            elif len(original_curr_root.children) == 1:
                child = original_curr_root.children.pop()
                original_curr_root.children.add(child)

                child_in_new_tableau = new_tableau.is_child_in_tableau(child)
                if child_in_new_tableau:
                    child_in_new_tableau.parents.add(new_curr_root)
                    new_curr_root.children.add(child_in_new_tableau)
                    return new_tableau, new_curr_root

                new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(), node_type=child.node_type,
                                initial=child.initial, formulas=child.formulas, node_id=child.id)
                new_curr_root.children.add(new_node)
                new_curr_root = new_node
                original_curr_root = child
                continue

            else:  # len(original_curr_root.children) > 1
                child = self.find_child_to_handle(original_curr_root.children)
                new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                node_type=child.node_type, initial=child.initial,
                                formulas=child.formulas, node_id=child.id)
                new_curr_root.children.add(new_node)
                new_curr_root = new_node
                original_curr_root = child
                continue

    def is_open(self):
        for state in self.states.values():
            if state.initial:
                return True
        return False
