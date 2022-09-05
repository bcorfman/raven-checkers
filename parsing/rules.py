import re
import sys


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
    # there must be no : in front of the
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
            self.wiki = u'''(?P<wiki>[%s]\\w+[%s]\\w+)''' % (up_case, up_case)
            inline_elements.insert(3, self.wiki)
        self.inline_re = c('|'.join(inline_elements), re.X | re.U)
