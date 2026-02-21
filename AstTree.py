import matplotlib.pyplot as plt

class ASTDrawer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(16, 10))
        self.ax.axis('off')
        self.x = 0
        self.y = 0
        self.positions = {}
        self.edges = []
        self.node_id = 0

    def draw(self, ast):
        root_id = self._walk(ast, depth=0)
        self._render()
        plt.show()

    def _walk(self, node, depth):
        my_id = self.node_id
        self.node_id += 1

        label = self._label(node)

        # موقعیت گره
        x = self.x
        y = -depth
        self.positions[my_id] = (x, y, label)
        self.x += 1

        # پردازش بچه‌ها
        children = self._children(node)
        for child in children:
            child_id = self._walk(child, depth + 1)
            self.edges.append((my_id, child_id))

        return my_id

    def _label(self, node):
        if isinstance(node, tuple):
            return node[0]
        elif isinstance(node, list):
            return "list"
        else:
            return str(node)

    def _children(self, node):
        if isinstance(node, tuple):
            return [x for x in node[1:] if x is not None]
        elif isinstance(node, list):
            return node
        else:
            return []

    def _render(self):
        # رسم یال‌ها
        for parent, child in self.edges:
            x1, y1, _ = self.positions[parent]
            x2, y2, _ = self.positions[child]
            self.ax.plot([x1, x2], [y1, y2], 'g-')

        # رسم گره‌ها
        for _, (x, y, label) in self.positions.items():
            self.ax.text(
                x, y, label,
                bbox=dict(boxstyle="round", fc="skyblue"),
                ha='center'
            )
