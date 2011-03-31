from Tkinter import PhotoImage
from Tkconstants import *
from globalconst import BULLET_IMAGE
from creoleparser import Parser
from rules import LinkRules

class TextTagEmitter(object):
    """
    Generate tagged output compatible with the Tkinter Text widget
    """
    def __init__(self, root, txtWidget, hyperMgr, bulletImage,
                 link_rules=None):
        self.root = root
        self.link_rules = link_rules or LinkRules()
        self.txtWidget = txtWidget
        self.hyperMgr = hyperMgr
        self.line = 1
        self.index = 0
        self.number = 1
        self.bullet = False
        self.bullet_image = bulletImage
        self.begin_italic = ''
        self.begin_bold = ''
        self.begin_list_item = ''
        self.list_item = ''
        self.begin_link = ''

    # visit/leave methods for emitting nodes of the document:
    def visit_document(self, node):
        pass

    def leave_document(self, node):
        # leave_paragraph always leaves two extra carriage returns at the
        # end of the text. This deletes them.
        txtindex = '%d.%d' % (self.line-1, self.index)
        self.txtWidget.delete(txtindex, END)

    def visit_text(self, node):
        if self.begin_list_item:
            self.list_item = node.content
        elif self.begin_link:
            pass
        else:
            txtindex = '%d.%d' % (self.line, self.index)
            self.txtWidget.insert(txtindex, node.content)

    def leave_text(self, node):
        if not self.begin_list_item:
            self.index += len(node.content)

    def visit_separator(self, node):
        raise NotImplementedError

    def leave_separator(self, node):
        raise NotImplementedError

    def visit_paragraph(self, node):
        pass

    def leave_paragraph(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n\n')
        self.line += 2
        self.index = 0
        self.number = 1

    def visit_bullet_list(self, node):
        self.bullet = True

    def leave_bullet_list(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n')
        self.line += 1
        self.index = 0
        self.bullet = False

    def visit_number_list(self, node):
        self.number = 1

    def leave_number_list(self, node):
        txtindex = '%d.%d' % (self.line, self.index)
        self.txtWidget.insert(txtindex, '\n')
        self.line += 1
        self.index = 0

    def visit_list_item(self, node):
        self.begin_list_item = '%d.%d' % (self.line, self.index)

    def leave_list_item(self, node):
        if self.bullet:
            self.txtWidget.insert(self.begin_list_item, '\t')
            next = '%d.%d' % (self.line, self.index+1)
            self.txtWidget.image_create(next, image=self.bullet_image)
            next = '%d.%d' % (self.line, self.index+2)
            content = '\t%s\t\n' % self.list_item
            self.txtWidget.insert(next, content)
            end_list_item = '%d.%d' % (self.line, self.index + len(content)+2)
            self.txtWidget.tag_add('bullet', self.begin_list_item, end_list_item)
        elif self.number:
            content = '\t%d.\t%s\n' % (self.number, self.list_item)
            end_list_item = '%d.%d' % (self.line, self.index + len(content))
            self.txtWidget.insert(self.begin_list_item, content)
            self.txtWidget.tag_add('number', self.begin_list_item, end_list_item)
            self.number += 1
        self.begin_list_item = ''
        self.list_item = ''
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
        # TODO: Revisit unicode encode/decode issues later.
        # 1. Decode early.  2. Unicode everywhere  3. Encode late
        # However, decoding filename and link_text here works for now.
        fname = str(node.content).replace('%20', ' ')
        link_text = str(node.children[0].content).replace('%20', ' ')
        self.txtWidget.insert(self.begin_link, link_text,
                              self.hyperMgr.add(fname))
        self.begin_link = ''

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
    def __init__(self, txtWidget, hyperMgr):
        self.txt = txtWidget
        self.hyperMgr = hyperMgr
        self.bullet_image = PhotoImage(file=BULLET_IMAGE)
        self._reset()

    def _reset(self):
        self.number = 0
        self.bullet = False
        self.filename = ''
        self.link_start = False
        self.first_tab = True
        self.list_end = False

    def dump(self, index1='1.0', index2=END):
        # outputs contents from Text widget in Creole format.
        creole = ''
        self._reset()
        for key, value, index in self.txt.dump(index1, index2):
            if key == 'tagon':
                if value == 'bold':
                    creole += '**'
                elif value == 'italic':
                    creole += '//'
                elif value == 'bullet':
                    creole += '*'
                    self.bullet = True
                    self.list_end = False
                elif value.startswith('hyper-'):
                    self.filename = self.hyperMgr.filenames[value]
                    self.link_start = True
                elif value == 'number':
                    creole += '#'
                    self.number += 1
            elif key == 'tagoff':
                if value == 'bold':
                    creole += '**'
                elif value == 'italic':
                    creole += '//'
                elif value.startswith('hyper-'):
                    creole += ']]'
                elif value == 'number':
                    numstr = '#\t%d.\t' % self.number
                    if numstr in creole:
                        creole = creole.replace(numstr, '# ', 1)
                    self.list_end = True
                elif value == 'bullet':
                    creole = creole.replace('\n*\t\t', '\n* ', 1)
                    self.bullet = False
                    self.list_end = True
            elif key == 'text':
                if self.link_start:
                    # TODO: Revisit unicode encode/decode issues later.
                    # 1. Decode early.  2. Unicode everywhere  3. Encode late
                    # However, encoding filename and link_text here works for
                    # now.
                    fname = self.filename.replace(' ', '%20').encode('utf-8')
                    link_text = value.replace(' ', '%20')
                    value = '[[%s|%s' % (fname, link_text)
                    self.link_start = False
                numstr = '%d.\t' % self.number
                if self.list_end and value != '\n' and numstr not in value:
                    creole += '\n'
                    self.number = 0
                    self.list_end = False
                creole += value
        return creole.rstrip()

    def restore(self, creole):
        self.hyperMgr.reset()
        document = Parser(unicode(creole, 'utf-8', 'ignore')).parse()
        return TextTagEmitter(document, self.txt, self.hyperMgr,
                              self.bullet_image).emit()
