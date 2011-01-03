from Tkconstants import *
from creoleparser import Parser
from rules import LinkRules

class TextTagEmitter(object):
    """
    Generate tagged output compatible with the Tkinter Text widget
    """
    def __init__(self, root, txtWidget, link_rules=None):
        self.root = root
        self.link_rules = link_rules or LinkRules()
        self.txtWidget = txtWidget
        self.line = 1
        self.index = 0
        self.number = 1
        self.begin_italic = ''
        self.begin_bold = ''

    # visit/leave methods for emitting nodes of the document:
    def visit_document(self, node):
        pass

    def leave_document(self, node):
        pass

    def visit_text(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, node.content)

    def leave_text(self, node):
        self.index += len(node.content)

    def visit_separator(self, node):
        raise NotImplementedError

    def leave_separator(self, node):
        raise NotImplementedError

    def visit_paragraph(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n\n')

    def leave_paragraph(self, node):
        self.line += 2
        self.index = 0
        self.number = 1

    def visit_bullet_list(self, node):
        raise NotImplementedError

    def leave_bullet_list(self, node):
        raise NotImplementedError

    def visit_number_list(self, node):
        self.number = 1

    def leave_number_list(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n')
        self.line += 1
        self.number = 0

    def visit_list_item(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        val = '%d.' % self.number
        self.txtWidget.insert(txtindex, val)
        self.index += len(val)

    def leave_list_item(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n')
        self.number += 1
        self.line += 1
        self.index = 0

    def visit_emphasis(self, node):
        self.begin_italic = '%d.%d' % (self.line, self.index)

    def leave_emphasis(self, node):
        end_italic = '%d.%d' % (self.line, self.index)
        self.txtWidget.tag_add('italic', self.begin_italic, end_italic)

    def visit_strong(self, node):
        self.begin_bold = '%d.%d' % (self.line, self.index)

    def leave_strong(self, node):
        end_bold = '%d.%d' % (self.line, self.index)
        self.txtWidget.tag_add('bold', self.begin_bold, end_bold)

    def visit_link(self, node):
        self.begin_link = '%d.%d' % (self.line, self.index)

    def leave_link(self, node):
        end_link = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(self.begin_link, node.content,
                              self.hyperMgr.add(node.content))

    def visit_break(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n')

    def leave_break(self, node):
        self.line += 1
        self.index = 0

    def visit_default(self, node):
        """Fallback function for visiting unknown nodes."""
        raise TypeError

    def leave_default(self, node):
        """Fallback function for leaving unknown nodes."""
        raise TypeError

    def emit_children(self, node):
        """Emit all the children of a node."""
        for child in node.children:
            self.emit_node(child)

    def emit_node(self, node):
        """Visit/depart a single node and its children."""
        visit = getattr(self, 'visit_%s' % node.kind, self.visit_default)
        visit(node)
        self.emit_children(node)
        leave = getattr(self, 'leave_%s' % node.kind, self.leave_default)
        leave(node)

    def emit(self):
        """Emit the document represented by self.root DOM tree."""
        return self.emit_node(self.root)

class Serializer(object):
    def __init__(self, txtWidget):
        self.txt = txtWidget

    def dump(self, index1='1.0', index2=END):
        # outputs contents from Text widget in Creole format.
        creole = ''
        tags = {}
        try:
            for key, value, index in self.txt.dump(index1, index2):
                if key == 'tagon':
                    if value == 'bold':
                        creole += '**'
                    elif value == 'italic':
                        creole += '//'
                    elif value == 'bullet':
                        creole += '*'
                    elif value == 'link':
                        if not tags.get(value):
                            tagname = value
                            tags[tagname] = []
                            for item in self.txt.tag_configure(tagname):
                                value = item[4]
                                if len(value) > 0:
                                    option = item[0]
                                    tags[tagname].append((option, value))
                elif key == 'tagoff':
                    if value == 'bold':
                        creole += '**'
                    elif value == 'italic':
                        creole += '//'
                    elif value == 'link':
                        creole += '<link>'
                elif key == 'text':
                    creole += value.replace('\n', r'\\')
        finally:
            return creole

    def restore(self, creole):
        document = Parser(unicode(creole, 'utf-8', 'ignore')).parse()
        return TextTagEmitter(document, self.txt).emit()
