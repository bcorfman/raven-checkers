#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable-all
# Creole parser/HTML converter, from http://devel.sheep.art.pl/creole/.
# Copyright 2007 by Radomir Dopieralski. Licensed under the BSD license.

import re
import sys


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


class LinkRules(object):
    """Rules for recognizing external links."""

    # For the link targets:
    proto = r'http|https|ftp|nntp|news|mailto|telnet|file|irc'
    extern = r'(?P<extern_addr>(?P<extern_proto>%s):.*)' % proto
    interwiki = r'''
            (?P<inter_wiki> [A-Z][a-zA-Z]+ ) :
            (?P<inter_page> .* )
        '''

    def __init__(self):
        self.addr_re = re.compile('|'.join([
                self.extern,
                self.interwiki,
            ]), re.X | re.U)  # for addresses


class Rules(object):
    """Hold all the rules for generating regular expressions."""

    # For the inline elements:
    proto = r'http|https|ftp|nntp|news|mailto|telnet|file|irc'
    link = r'''(?P<link>
            \[\[
            (?P<link_target>.+?) \s*
            ([|] \s* (?P<link_text>.+?) \s*)?
            ]]
        )'''
    image = r'''(?P<image>
            {{
            (?P<image_target>.+?) \s*
            ([|] \s* (?P<image_text>.+?) \s*)?
            }}
        )'''
    macro = r'''(?P<macro>
            <<
            (?P<macro_name> \w+)
            (\( (?P<macro_args> .*?) \))? \s*
            ([|] \s* (?P<macro_text> .+?) \s* )?
            >>
        )'''
    code = r'(?P<code> {{{ (?P<code_text>.*?) }}} )'
    # there must be no : in front of the //
    # avoids italic rendering in urls with
    # unknown protocols
    emph = r'(?P<emph> (?<!:)// )'
    strong = r'(?P<strong> \*\* )'
    linebreak = r'(?P<break> \\\\ )'
    escape = r'(?P<escape> ~ (?P<escaped_char>\S) )'
    char = r'(?P<char> . )'

    # For the block elements:
    separator = r'(?P<separator> ^ \s* ---- \s* $ )'  # horizontal line
    line = r'(?P<line> ^ \s* $ )'  # empty line that separates paragraphs
    head = r'''(?P<head>
            ^ \s*
            (?P<head_head>=+) \s*
            (?P<head_text> .*? ) \s*
            (?P<head_tail>=*) \s*
            $
        )'''
    text = r'(?P<text> .+ )'
    list = r'''(?P<list>
            ^ [ \t]* ([*][^*\#]|[\#][^\#*]).* $
            ( \n[ \t]* [*\#]+.* $ )*
        )'''  # Matches the whole list, separate items are parsed later. The list *must* start with a single bullet.
    item = r'''(?P<item>
            ^ \s*
            (?P<item_head> [\#*]+) \s*
            (?P<item_text> .*?)
            $
        )'''  # Matches single list items
    pre = r'''(?P<pre>
            ^{{{ \s* $
            (\n)?
            (?P<pre_text>
                ([\#]!(?P<pre_kind>\w*?)(\s+.*)?$)?
                (.|\n)+?
            )
            (\n)?
            ^}}} \s*$
        )'''
    pre_escape = r' ^(?P<indent>\s*) ~ (?P<rest> \}\}\} \s*) $'
    table = r'''(?P<table>
            ^ \s*
            [|].*? \s*
            [|]? \s*
            $
        )'''

    # For splitting table cells:
    cell = r'''
            \| \s*
            (
                (?P<head> [=][^|]+ ) |
                (?P<cell> (  %s | [^|])+ )
            ) \s*
        ''' % '|'.join([link, macro, image, code])

    def __init__(self, bloglike_lines=False, url_protocols=None,
                 wiki_words=False):
        c = re.compile
        # For pre escaping, in creole 1.0 done with ~:
        self.pre_escape_re = c(self.pre_escape, re.M | re.X)
        # for link descriptions
        self.link_re = c('|'.join([self.image, self.linebreak,
                                   self.char]), re.X | re.U)
        # for list items
        self.item_re = c(self.item, re.X | re.U | re.M)
        # for table cells
        self.cell_re = c(self.cell, re.X | re.U)

        # For block elements:
        if bloglike_lines:
            self.text = r'(?P<text> .+ ) (?P<break> (?<!\\)$\n(?!\s*$) )?'
        self.block_re = c('|'.join([self.line, self.head, self.separator,
                                    self.pre, self.list, self.table,
                                    self.text]), re.X | re.U | re.M)

        # For inline elements:
        if url_protocols is not None:
            self.proto = '|'.join(re.escape(p) for p in url_protocols)
        self.url = r'''(?P<url>
            (^ | (?<=\s | [.,:;!?()/=]))
            (?P<escaped_url>~)?
            (?P<url_target> (?P<url_proto> %s ):\S+? )
            ($ | (?=\s | [,.:;!?()] (\s | $))))''' % self.proto
        inline_elements = [self.link, self.url, self.macro,
                           self.code, self.image, self.strong,
                           self.emph, self.linebreak,
                           self.escape, self.char]
        if wiki_words:
            import unicodedata
            up_case = u''.join(chr(i) for i in range(sys.maxunicode)
                               if unicodedata.category(chr(i)) == 'Lu')
            self.wiki = r'(?P<wiki>[%s]\w+[%s]\w+)' % (up_case, up_case)
            inline_elements.insert(3, self.wiki)
        self.inline_re = c('|'.join(inline_elements), re.X | re.U)


class Parser(object):
    """
    Parse the raw text and create a document object
    that can be converted into output using Emitter.

    A separate instance should be created for parsing a new document.
    The first parameter is the raw text to be parsed. An optional second
    argument is the Rules object to use. You can customize the parsing
    rules to enable optional features or extend the parser.
    """

    def __init__(self, raw, rules=None):
        self.rules = rules or Rules()
        self.raw = raw
        self.root = DocNode('document', None)
        self.cur = self.root        # The most recent document node
        self.text = None            # The node to add inline characters to

    def _upto(self, node, kinds):
        """
        Look up the tree to the first occurrence
        of one of the listed kinds of nodes or root.
        Start at the node 'node'.
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
        """Handles images and attachemnts included in the page."""

        target = groups.get('image_target', '').strip()
        text = (groups.get('image_text', '') or '').strip()
        node = DocNode("image", self.cur, target)
        DocNode('text', node, text or node.content)
        self.text = None

    def _separator_repl(self, _):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
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
        while (lst and not (lst.kind in ('number_list', 'bullet_list') and
                            lst.level == level) and lst.kind not in ('document', 'section', 'blockquote')):
            lst = lst.parent
        if lst and lst.kind == kind:
            self.cur = lst
        else:
            # Create a new level of list
            self.cur = self._upto(self.cur, ('list_item', 'document', 'section', 'blockquote'))
            self.cur = DocNode(kind, self.cur)
            self.cur.level = level
        self.cur = DocNode('list_item', self.cur)
        self.parse_inline(text)
        self.text = None

    def _list_repl(self, groups):
        text = groups.get('list', u'')
        self.parse_re(text, self.rules.item_re)

    def _head_repl(self, groups):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        node = DocNode('header', self.cur, groups.get('head_text', '').strip())
        node.level = len(groups.get('head_head', ' '))

    def _text_repl(self, groups):
        text = groups.get('text', '')
        if self.cur.kind in ('table', 'table_row', 'bullet_list', 'number_list'):
            self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        if self.cur.kind in ('document', 'section', 'blockquote'):
            self.cur = DocNode('paragraph', self.cur)
        else:
            text = u' ' + text
        self.parse_inline(text)
        if groups.get('break') and self.cur.kind in ('paragraph', 'emphasis', 'strong', 'code'):
            DocNode('break', self.cur, '')
        self.text = None
    _break_repl = _text_repl

    def _table_repl(self, groups):
        row = groups.get('table', '|').strip()
        self.cur = self._upto(self.cur, (
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
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))
        kind = groups.get('pre_kind', None)
        text = groups.get('pre_text', u'')

        def remove_tilde(m):
            return m.group('indent') + m.group('rest')
        text = self.rules.pre_escape_re.sub(remove_tilde, text)
        node = DocNode('preformatted', self.cur, text)
        node.sect = kind or ''
        self.text = None

    def _line_repl(self, _):
        self.cur = self._upto(self.cur, ('document', 'section', 'blockquote'))

    def _code_repl(self, groups):
        DocNode('code', self.cur, groups.get('code_text', u'').strip())
        self.text = None

    def _emph_repl(self, _):
        if self.cur.kind != 'emphasis':
            self.cur = DocNode('emphasis', self.cur)
        else:
            self.cur = self._upto(self.cur, ('emphasis', )).parent
        self.text = None

    def _strong_repl(self, _):
        if self.cur.kind != 'strong':
            self.cur = DocNode('strong', self.cur)
        else:
            self.cur = self._upto(self.cur, ('strong', )).parent
        self.text = None

    def _break_repl(self, _):
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
        """Parse the text given as "self.raw" and return DOM tree."""
        self.parse_re(self.raw, self.rules.block_re)
        return self.root


class HtmlEmitter(object):
    """
    Generate HTML output for the document
    tree consisting of DocNodes.
    """

    def __init__(self, root, id_func, link_rules=None):
        self.root = root
        self.id_func = id_func
        self.headers = []
        self.link_rules = link_rules or LinkRules()

    def get_text(self, node):
        """Try to emit whatever text is in the node."""
        try:
            return node.children[0].content or ''
        except (IndexError, AttributeError):
            return node.content or ''

    def html_escape(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def attr_escape(self, text):
        return self.html_escape(text).replace('"', '&quot')

    # *_emit methods for emitting nodes of the document:

    def document_emit(self, node):
        return self.emit_children(node)

    def text_emit(self, node):
        return self.html_escape(node.content)

    def separator_emit(self, _):
        return u'<hr>'

    def paragraph_emit(self, node):
        return u'<p>%s</p>\n' % self.emit_children(node)

    def bullet_list_emit(self, node):
        return u'<ul>\n%s</ul>\n' % self.emit_children(node)

    def number_list_emit(self, node):
        return u'<ol>\n%s</ol>\n' % self.emit_children(node)

    def list_item_emit(self, node):
        return u'<li>%s</li>\n' % self.emit_children(node)

    def table_emit(self, node):
        return u'<table>\n%s</table>\n' % self.emit_children(node)

    def table_row_emit(self, node):
        return u'<tr>%s</tr>\n' % self.emit_children(node)

    def table_cell_emit(self, node):
        return u'<td>%s</td>' % self.emit_children(node)

    def table_head_emit(self, node):
        return u'<th>%s</th>' % self.emit_children(node)

    def emphasis_emit(self, node):
        return u'<i>%s</i>' % self.emit_children(node)

    def strong_emit(self, node):
        return u'<b>%s</b>' % self.emit_children(node)

    def header_emit(self, node):
        hid = self.id_func()
        content = self.html_escape(node.content)
        self.headers.append((node.level, content, hid))
        return u'<h%d id="%s">%s</h%d>\n' % (
            node.level, hid, content, node.level)

    def code_emit(self, node):
        return u'<tt>%s</tt>' % self.html_escape(node.content)

    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        m = self.link_rules.addr_re.match(target)
        if m:
            if m.group('extern_addr'):
                return u'<a href="%s">%s</a>' % (
                    self.attr_escape(target), inside)
            elif m.group('inter_wiki'):
                raise NotImplementedError
        return u'<a href="%s">%s</a>' % (
            self.attr_escape(target), inside)

    def image_emit(self, node):
        target = node.content
        text = self.get_text(node)
        m = self.link_rules.addr_re.match(target)
        if m:
            if m.group('extern_addr'):
                return u'<img src="%s" alt="%s">' % (
                    self.attr_escape(target), self.attr_escape(text))
            elif m.group('inter_wiki'):
                raise NotImplementedError
        return u'<img src="%s" alt="%s">' % (
            self.attr_escape(target), self.attr_escape(text))

    def macro_emit(self, node):
        raise NotImplementedError

    def break_emit(self, _):
        return u"<br>"

    def preformatted_emit(self, node):
        return u"<pre>%s</pre>" % self.html_escape(node.content)

    def default_emit(self, node):
        """Fallback function for emitting unknown nodes."""

        raise TypeError

    def emit_children(self, node):
        """Emit all the children of a node."""

        return u''.join([self.emit_node(child) for child in node.children])

    def emit_node(self, node):
        """Emit a single node."""
        emit = getattr(self, '%s_emit' % node.kind, self.default_emit)
        return emit(node)

    def emit(self):
        """Emit the document represented by "self.root" DOM tree."""
        return self.emit_node(self.root)


def translate(data, id_func):
    emitter = HtmlEmitter(Parser(data).parse(), id_func)
    html = emitter.emit()
    return html, emitter.headers
