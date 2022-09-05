class DocNode(object):
    """
    A node in the document.
    """

    def __init__(self, kind='', parent=None, content=None):
        self.children = []
        self.parent = parent
        self.kind = kind
        self.content = content
        if self.parent is not None:
            self.parent.children.append(self)
