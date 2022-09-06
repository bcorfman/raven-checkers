from parsing.rules import Rules
from parsing.document import DocNode


class Parser(object):
    """
    Parse the raw text and create a document obj
    that can be converted into output using Emitter.

    A separate instance should be created for parsing a new document.
    The first parameter is the raw text to be parsed. An optional second
    argument is the Rules obj to use. You can customize the parsing
    rules to enable optional features or extend the parser.
    """

    def __init__(self, raw, rules=None):
        self.rules = rules or Rules()
        self.raw = raw
        self.root = DocNode('document', None)
        self.cur = self.root        # The most recent document node
        self.text = None            # The node to add inline characters to

    def _up_to(self, node, kinds):
        """
        Look up the tree to the first occurrence
        of one of the listed kinds of nodes or root.
        Start at the node node.
        """
        while node.parent is not None and node.kind not in kinds:
            node = node.parent
        return node

    # The _*_repl methods called for matches in regexps. Sometimes the
    # same method needs several names, because of group names in regexps.

    def _url_repl(self, groups):
        """Handle raw urls in text."""

        if not groups.get('escaped_url'):
            # this url is NOT escaped
            target = groups.get('url_target', '')
            node = DocNode('link', self.cur)
            node.content = target
            DocNode('text', node, node.content)
            self.text = None
        else:
            # this url is escaped, we render it as text
            if self.text is None:
                self.text = DocNode('text', self.cur, u'')
            self.text.content += groups.get('url_target')

    def _link_repl(self, groups):
        """Handle all kinds of links."""

        target = groups.get('link_target', '')
        text = (groups.get('link_text', '') or '').strip()
        parent = self.cur
        self.cur = DocNode('link', self.cur)
        self.cur.content = target
        self.text = None
        self.parse_re(text, self.rules.link_re)
        self.cur = parent
        self.text = None

    def _wiki_repl(self, groups):
        """Handle WikiWord links, if enabled."""

        text = groups.get('wiki', '')
        node = DocNode('link', self.cur)
        node.content = text
        DocNode('text', node, node.content)
        self.text = None

    def _macro_repl(self, groups):
        """Handles macros using the placeholder syntax."""

        name = groups.get('macro_name', '')
        text = (groups.get('macro_text', '') or '').strip()
        node = DocNode('macro', self.cur, name)
        node.args = groups.get('macro_args', '') or ''
        DocNode('text', node, text or name)
        self.text = None

    def _image_repl(self, groups):
        """Handles images and attachments included in the page."""

        target = groups.get('image_target', '').strip()
        text = (groups.get('image_text', '') or '').strip()
        node = DocNode("image", self.cur, target)
        DocNode('text', node, text or node.content)
        self.text = None

    def _separator_repl(self, groups):
        self.cur = self._up_to(self.cur, ('document', 'section', 'blockquote'))
        DocNode('separator', self.cur)

    def _item_repl(self, groups):
        bullet = groups.get('item_head', u'')
        text = groups.get('item_text', u'')
        if bullet[-1] == '#':
            kind = 'number_list'
        else:
            kind = 'bullet_list'
        level = len(bullet)
        lst = self.cur
        # Find a list of the same kind and level up the tree
        while (lst and
               lst.kind not in ('number_list', 'bullet_list') or
               lst.level != level) and lst.kind not in ('document', 'section', 'blockquote'):
            lst = lst.parent
        if lst and lst.kind == kind:
            self.cur = lst
        else:
            # Create a new level of list
            self.cur = self._up_to(self.cur,
                                   ('list_item', 'document', 'section', 'blockquote'))
            self.cur = DocNode(kind, self.cur)
            self.cur.level = level
        self.cur = DocNode('list_item', self.cur)
        self.parse_inline(text)
        self.text = None

    def _list_repl(self, groups):
        text = groups.get('list', u'')
        self.parse_re(text, self.rules.item_re)

    def _head_repl(self, groups):
        self.cur = self._up_to(self.cur, ('document', 'section', 'blockquote'))
        node = DocNode('header', self.cur, groups.get('head_text', '').strip())
        node.level = len(groups.get('head_head', ' '))

    def _text_repl(self, groups):
        text = groups.get('text', '')
        if self.cur.kind in ('table', 'table_row', 'bullet_list', 'number_list'):
            self.cur = self._up_to(self.cur,
                                   ('document', 'section', 'blockquote'))
        if self.cur.kind in ('document', 'section', 'blockquote'):
            self.cur = DocNode('paragraph', self.cur)
        else:
            text = u' ' + text
        self.parse_inline(text)
        if groups.get('break') and self.cur.kind in ('paragraph', 'emphasis', 'strong', 'code'):
            DocNode('break', self.cur, '')
        self.text = None
    # _break_repl = _text_repl

    def _table_repl(self, groups):
        row = groups.get('table', '|').strip()
        self.cur = self._up_to(self.cur, (
            'table', 'document', 'section', 'blockquote'))
        if self.cur.kind != 'table':
            self.cur = DocNode('table', self.cur)
        tb = self.cur
        tr = DocNode('table_row', tb)

        for m in self.rules.cell_re.finditer(row):
            cell = m.group('cell')
            if cell:
                self.cur = DocNode('table_cell', tr)
                self.text = None
                self.parse_inline(cell)
            else:
                cell = m.group('head')
                self.cur = DocNode('table_head', tr)
                self.text = DocNode('text', self.cur, u'')
                self.text.content = cell.strip('=')
        self.cur = tb
        self.text = None

    def _pre_repl(self, groups):
        self.cur = self._up_to(self.cur, ('document', 'section', 'blockquote'))
        kind = groups.get('pre_kind', None)
        text = groups.get('pre_text', u'')

        def remove_tilde(m):
            return m.group('indent') + m.group('rest')
        text = self.rules.pre_escape_re.sub(remove_tilde, text)
        node = DocNode('preformatted', self.cur, text)
        node.sect = kind or ''
        self.text = None

    def _line_repl(self, groups):
        self.cur = self._up_to(self.cur, ('document', 'section', 'blockquote'))

    def _code_repl(self, groups):
        DocNode('code', self.cur, groups.get('code_text', u'').strip())
        self.text = None

    def _emph_repl(self, groups):
        if self.cur.kind != 'emphasis':
            self.cur = DocNode('emphasis', self.cur)
        else:
            self.cur = self._up_to(self.cur, ('emphasis',)).parent
        self.text = None

    def _strong_repl(self, groups):
        if self.cur.kind != 'strong':
            self.cur = DocNode('strong', self.cur)
        else:
            self.cur = self._up_to(self.cur, ('strong',)).parent
        self.text = None

    def _break_repl(self, groups):
        DocNode('break', self.cur, None)
        self.text = None

    def _escape_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u'')
        self.text.content += groups.get('escaped_char', u'')

    def _char_repl(self, groups):
        if self.text is None:
            self.text = DocNode('text', self.cur, u'')
        self.text.content += groups.get('char', u'')

    def parse_inline(self, raw):
        """Recognize inline elements inside blocks."""

        self.parse_re(raw, self.rules.inline_re)

    def parse_re(self, raw, rules_re):
        """Parse a fragment according to the compiled rules."""

        for match in rules_re.finditer(raw):
            groups = dict((k, v) for (k, v)
                          in match.groupdict().items()
                          if v is not None)
            name = match.lastgroup
            function = getattr(self, '_%s_repl' % name)
            function(groups)

    def parse(self):
        """Parse the text given as self.raw and return DOM tree."""

        self.parse_re(self.raw, self.rules.block_re)
        return self.root
