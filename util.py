class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    
    
    def __init__(self):
        self.frontier = []
        # Create set to improve searching of node explored
        self.node_state = set()
        # Create a dict for all nodes to optimize search
        self.nodes = {}    

    def add(self, node):
        self.frontier.append(node)
        self.node_state.add(node.state)
        self.nodes[node.state] = node

    def contains_state(self, state):
        # return any(node.state == state for node in self.frontier)
        
        # --------- For a faster search -----------------
        return state in self.node_state

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node
        
    def get_node(self, state):
        return self.nodes[state]

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
