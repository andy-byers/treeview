#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import enum
import os
import stat
import sys


class BoxCharacterType(enum.Enum):
    LTEE = 0
    BEND = 1
    HBAR = 2
    VBAR = 3
    ECAP = 4


class BoxCharacters:
    ASCII_CHARS = (
        ('+', ) * 2,
        ("'", ) * 2,
        ('-', ) * 2,
        ('|', ) * 2,
        (' ', ) * 2,
        )

    FANCY_CHARS = (
        ('├', '┣'),
        ('└', '┗'),
        ('─', '━'),
        ('│', '┃'),
        ('╴', '╸'),
        )

    def __init__(self, use_thick=False, use_ascii=False):
        self.use_thick = use_thick
        self.use_ascii = use_ascii

    def __call__(self, char_type):
        chars = self.ASCII_CHARS if self.use_ascii else self.FANCY_CHARS
        return chars[char_type.value][self.use_thick]


class NodeType(enum.Enum):
    DIRECTORY = 1
    REGULAR_FILE = 2
    CHARACTER_DEVICE = 3
    BLOCK_DEVICE = 4
    FIFO = 5
    LINK = 6
    UNKNOWN = 7

    @classmethod
    def from_mode(cls, mode):
        if mode is None:
            return cls.DIRECTORY
        elif stat.S_ISREG(mode):
            return cls.REGULAR_FILE
        elif stat.S_ISCHR(mode):
            return cls.CHARACTER_DEVICE
        elif stat.S_ISBLK(mode):
            return cls.BLOCK_DEVICE
        elif stat.S_ISFIFO(mode):
            return cls.FIFO
        elif stat.S_ISLNK(mode):
            return cls.LINK
        else:
            return cls.UNKNOWN


class Node:
    def __init__(self, path):
        self.path = path
        self.type = None
        self.children = []

    @property
    def name(self):
        return self.path if self.is_placeholder() else os.path.basename(self.path)

    @classmethod
    def placeholder(cls, count):
        assert type(count) is int
        return cls(count)

    def is_placeholder(self):
        return type(self.path) is int


class FilesystemParser:
    def __init__(self, param):
        self.show_hidden = param['hidden']
        self.directories_only = param['directories']
        self.max_depth = param['level'] - 1
        self.child_limit = param['limit']

    def _make_nodes(self, directory):
        def get_path_or_overflow(x):
            if type(x) is str:
                return os.path.join(directory, x)
            else:
                return x
        entries = os.listdir(directory)
        # TODO: We could make what we sort on an input parameter.
        entries.sort()
        entries = [Node(get_path_or_overflow(x)) for x in entries]
        included = list(filter(lambda x: self._should_include(x), entries))
        overflow = len(included) - self.child_limit
        if overflow > 0:
            included = included[:-overflow]
        placeholder = [Node(overflow)] if overflow > 0 else []
        return included + placeholder

    def _should_include(self, node):
        if node.is_placeholder():
            return True
        return not node.name.startswith('.') or self.show_hidden

    def _build_structure(self, root, depth):
        if depth > self.max_depth:
            return root
        for node in self._make_nodes(root.path):
            if node.is_placeholder():
                root.children.append(node)
                continue
            # if self._should_exclude(node):
            #     continue
            path = os.path.join(root.path, node.name)
            mode = os.lstat(path).st_mode
            if stat.S_ISDIR(mode):
                node.type = NodeType.DIRECTORY
                root.children.append(self._build_structure(node, depth + 1))
            elif not self.directories_only:
                node.type = NodeType.from_mode(mode)
                root.children.append(node)
        return root

    def parse(self, path):
        root = Node(path)
        root.type = NodeType.DIRECTORY
        return self._build_structure(root, 0)


class Color(enum.Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class Colorizer:
    _COLORMAP = (
        Color.BLUE,
        Color.GREEN,
        Color.RED,
        Color.YELLOW,
        Color.MAGENTA,
        Color.CYAN,
        Color.WHITE,
        )

    _TEMPLATE = '\x1b[{}m'

    def __init__(self, is_enabled, is_colorful=True, is_bold=True):
        self.is_enabled = is_enabled
        self.is_colorful = is_colorful
        self.is_bold = is_bold

    @classmethod
    def type_to_color(cls, node_type):
        return cls._COLORMAP[node_type.value-1]

    @classmethod
    def get_code(cls, param):
        assert type(param) in (Color, NodeType)
        if type(param) is NodeType:
            param = cls.type_to_color(param)
        return str(param.value)

    def __call__(self, text, param):
        if self.is_enabled:
            codes = []
            if self.is_colorful:
                codes.append(self.get_code(param))
            if self.is_bold:
                codes.append('1')
            beg = Colorizer._TEMPLATE.format(';'.join(codes))
            end = Colorizer._TEMPLATE.format(0)
            text = beg + text + end
        return text


class TreeView:
    _PLACEHOLDER_TEMPLATE = '<{} more...>'

    def __init__(self, param):
        is_terminal = param['output'] == '<stdout>'
        self.colorizer = Colorizer(is_terminal, not param['nocolors'], param['bold'])
        self.width = param['width'] + param['ascii']
        self.indent = param['indent']
        self.chars = BoxCharacters(use_thick=param['thick'], use_ascii=param['ascii'])

    def _pad(self, has_pipe):
        if has_pipe:
            return self.chars(BoxCharacterType.VBAR) + ' ' * self.width
        else:
            return ' ' * (self.width+1)

    def _make_name(self, node, is_last):
        def make(start, end):
            bar = self.chars(BoxCharacterType.HBAR) * (self.width-1)
            return start + bar + self.chars(BoxCharacterType.ECAP) + end
        if node.is_placeholder():
            name = self.colorizer(self._PLACEHOLDER_TEMPLATE.format(node.name), Color.WHITE)
            return make(self.chars(BoxCharacterType.BEND), name)
        else:
            char = self.chars(BoxCharacterType.BEND) if is_last else self.chars(BoxCharacterType.LTEE)
            name = self.colorizer(node.name, node.type)
            return make(char, name)

    def _construct(self, root, prefix):
        output = []
        for i, node in enumerate(root.children):
            is_last = i == len(root.children) - 1
            output.append(prefix + self._make_name(node, is_last))
            if node.type == NodeType.DIRECTORY:
                output += self._construct(node, prefix + self._pad(not is_last))
        return output

    def construct(self, root):
        prefix = ' ' * self.indent
        result = self._construct(root, prefix)
        return '\n'.join([prefix + root.name] + result)


class Printer:
    def __init__(self, path):
        self.path = path

    def _print_to_file(self, message):
        with open(self.path, 'a') as f:
            print(message, file=f)

    def __call__(self, message):
        if self.path == '<stdout>':
            print(message)
        else:
            self._print_to_file(message)


FANCY_LEGEND_TEMPLATE = (
    ("┌─────────┬─────────┬─────────────────────────────────┐", ),
    ("│ Normal  │ Bold    │ Type                            │", ),
    ("├─────────┼─────────┼─────────────────────────────────┤", ),
    ("│ {} │ {} │ Directory                       │", Colorizer.type_to_color(NodeType.DIRECTORY)),
    ("│ {} │ {} │ Regular file                    │", Colorizer.type_to_color(NodeType.REGULAR_FILE)),
    ("│ {} │ {} │ Character special device        │", Colorizer.type_to_color(NodeType.CHARACTER_DEVICE)),
    ("│ {} │ {} │ Block special device            │", Colorizer.type_to_color(NodeType.BLOCK_DEVICE)),
    ("│ {} │ {} │ FIFO (named pipe)               │", Colorizer.type_to_color(NodeType.FIFO)),
    ("│ {} │ {} │ Symbolic link                   │", Colorizer.type_to_color(NodeType.LINK)),
    ("│ {} │ {} │ Unrecognized (door, port, etc.) │", Colorizer.type_to_color(NodeType.UNKNOWN)),
    ("└─────────┴─────────┴─────────────────────────────────┘", ),
)

ASCII_LEGEND_TEMPLATE = (
    (".---------.---------.---------------------------------.", ),
    ("| Normal  | Bold    | Type                            |", ),
    ("|---------|---------|---------------------------------|", ),
    ("| {} | {} | Directory                       |", Colorizer.type_to_color(NodeType.DIRECTORY)),
    ("| {} | {} | Regular file                    |", Colorizer.type_to_color(NodeType.REGULAR_FILE)),
    ("| {} | {} | Character special device        |", Colorizer.type_to_color(NodeType.CHARACTER_DEVICE)),
    ("| {} | {} | Block special device            |", Colorizer.type_to_color(NodeType.BLOCK_DEVICE)),
    ("| {} | {} | FIFO (named pipe)               |", Colorizer.type_to_color(NodeType.FIFO)),
    ("| {} | {} | Symbolic link                   |", Colorizer.type_to_color(NodeType.LINK)),
    ("| {} | {} | Unrecognized (door, port, etc.) |", Colorizer.type_to_color(NodeType.UNKNOWN)),
    ("'---------'---------'---------------------------------'", ),
)


def show_color_legend(use_ascii=False):
    colorizer = Colorizer(True, is_colorful=True, is_bold=False)
    bold_colorizer = Colorizer(True, is_colorful=True, is_bold=True)
    legend = ASCII_LEGEND_TEMPLATE if use_ascii else FANCY_LEGEND_TEMPLATE
    widest = max(len(c.name) for c in Color)
    output = []
    for template, *rest in legend:
        color = rest[0] if rest else Color.WHITE
        text = color.name.ljust(widest)
        normal = colorizer(text, color)
        bold = bold_colorizer(text, color)
        output.append(template.format(normal, bold))
    print('\n'.join(output))


def fatal(message):
    print(f'Error: {message}', file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Print a tree view of a directory.')
    parser.add_argument('path', type=str, default='.', nargs='?',
                        help='Path to a directory to view')
    parser.add_argument('-o', '--output', type=str, default='<stdout>',
                        help='Output to the specified file')
    parser.add_argument('-L', '--level', type=int, default=12,
                        help='Show this many tree levels')
    parser.add_argument('-n', '--limit', type=int, default=20,
                        help='Maximum number of entries to display in a directory')
    parser.add_argument('-I', '--indent', type=int, default=0,
                        help='Number of whitespace characters preceding the trunk')
    parser.add_argument('-w', '--width', type=int, default=1,
                        help='Width of the connection from an entry to the trunk')
    parser.add_argument('-c', '--nocolors', action='store_true',
                        help='Supress colors in terminal mode')
    parser.add_argument('-t', '--thick', action='store_true',
                        help='Use thicker box drawing characters')
    parser.add_argument('-b', '--bold', action='store_true',
                        help='Use bold characters')
    parser.add_argument('-d', '--directories', action='store_true',
                        help='Only show directories')
    parser.add_argument('-a', '--hidden', action='store_true',
                        help='Show hidden entries')
    parser.add_argument('-A', '--ascii', action='store_true',
                        help='Use only ascii characters')
    parser.add_argument('-H', '--legend', action='store_true',
                        help='Show the color legend and quit')
    args = parser.parse_args(sys.argv[1:])

    if args.legend:
        show_color_legend(args.ascii)
        return

    if not os.path.isdir(args.path):
        fatal(f'path "{args.path}" must refer to a directory')

    if args.output != '<stdout>':
        args.nocolors = True
        args.bold = False

    def check_bounds(name, value, bounds):
        lower, upper = bounds
        if value not in range(lower, upper + 1):
            fatal(f'{name} "{value}" must be ∈ [{lower}, {upper}]')

    check_bounds('level', args.level, (1, 15))
    check_bounds('limit', args.limit, (1, 40))
    check_bounds('width', args.width, (1, 80))
    check_bounds('indent', args.indent, (0, 80))

    try:
        parser = FilesystemParser(args.__dict__)
        root = parser.parse(args.path)
        view = TreeView(args.__dict__)
        printer = Printer(args.output)
        printer(view.construct(root))

    except Exception as error:
        # fatal(error)
        raise


if __name__ == '__main__':
    main()
