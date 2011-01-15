from Tkconstants import *
from parser import Parser

from parser import Parser
from rules import LinkRules


class TextTagEmitter(object):
    """
    Generate tagged output compatible with the Tkinter Text widget
    """

    def __init__(self, root, link_rules=None):
        self.root = root
        self.link_rules = link_rules or LinkRules()

    # *_emit methods for emitting nodes of the document:
    def document_emit(self, node):
        return self.emit_children(node)

    def text_emit(self, node):
        return node.content

    def separator_emit(self, node):
        raise NotImplementedError

    def paragraph_emit(self, node):
        return u'%s\n' % self.emit_children(node)

    def bullet_list_emit(self, node):
        return self.emit_children(node)

    def number_list_emit(self, node):
        return self.emit_children(node)

    def list_item_emit(self, node):
        return self.emit_children(node)

    def table_emit(self, node):
        raise NotImplementedError

    def table_row_emit(self, node):
        raise NotImplementedError

    def table_cell_emit(self, node):
        raise NotImplementedError

    def table_head_emit(self, node):
        raise NotImplementedError

    def emphasis_emit(self, node):
        return [('tagon','italics',node.index), self.emit_children(node),
                ('tagoff','italics',node.index)]

    def strong_emit(self, node):
        return [('tagon','bold',node.index), self.emit_children(node),
                ('tagoff','bold',node.index)]

    def header_emit(self, node):
        raise NotImplementedError

    def code_emit(self, node):
        raise NotImplementedError

    def link_emit(self, node):
        return ''

    def image_emit(self, node):
        raise NotImplementedError

    def macro_emit(self, node):
        raise NotImplementedError

    def break_emit(self, node):
        raise NotImplementedError

    def preformatted_emit(self, node):
        raise NotImplementedError

    def default_emit(self, node):
        """Fallback function for emitting unknown nodes."""
        raise TypeError

    def emit_children(self, node):
        """Emit all the children of a node."""
        return u''.join([self.emit_node(child) for child in node.children])

def dump_text_widget_to_rst(txtWidget, index1='1.0', index2=END):
    # outputs contents from Text widget in RestructuredText format.
    rst = ""
    tags = {}
    try:
        for key, value, index in txtWidget.dump(index1, index2):
            if key == 'tagon':
                if value == 'bold':
                    rst += '**'
                elif value == 'italic':
                    rst += '*'
                elif value == 'bullet':
                    rst += '-'
                elif value == 'link':
                    if not tags.get(value):
                        tagname = value
                        tags[tagname] = []
                        for item in txtWidget.tag_configure(tagname):
                            value = item[4]
                            if len(value) > 0:
                                option = item[0]
                                tags[tagname].append((option, value))
            elif key == 'tagoff':
                if value == 'bold':
                    rst += '**'
                elif value == 'italic':
                    rst += '*'
                elif value == 'link':
                    rst += '<link>'
            elif key == 'text':
                rst += value
    finally:
        return rst

def restore_text_widget_from_rst(rst, txtWidget):
    document = Parser(unicode(rst, 'utf-8', 'ignore')).parse()
    return TextTagEmitter(document).emit().encode('utf-8', 'ignore')
