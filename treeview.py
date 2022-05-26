#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import stat
import sys


class BoxDrawingCharacters:
    LTEE = ('├', '┣')
    BEND = ('└', '┗')
    HBAR = ('─', '━')
    VBAR = ('│', '┃')
    ECAP = ('╴', '╸')
    HDOTS = '⋯'
    VDOTS = '⁞'

    def __init__(self, bold):
        self.bold = bold

    def ltee(self):
        return BoxDrawingCharacters.LTEE[self.bold]

    def bend(self):
        return BoxDrawingCharacters.BEND[self.bold]

    def hbar(self):
        return BoxDrawingCharacters.HBAR[self.bold]

    def vbar(self):
        return BoxDrawingCharacters.VBAR[self.bold]

    def ecap(self):
        return BoxDrawingCharacters.ECAP[self.bold]

    def hdots(self):
        return BoxDrawingCharacters.HDOTS

    def vdots(self):
        return BoxDrawingCharacters.VDOTS


class Node:
    def __init__(self, name, mode=None):
        self.name = name
        self.mode = mode
        self.position = None
        self.index = None
        self.level = None
        self.weight = None
        self.parent = None
        self.children = []


def compute_tree_data(root, max_depth, max_breadth):
    def compute(directory, data, depth):
        nonlocal max_depth
        nonlocal max_breadth
        group = []
        subdirs = [None] if depth > max_depth else os.listdir(directory)
        if len(subdirs) > max_breadth:
            head = subdirs[:max_breadth-1]
            tail = [subdirs[-1]]
            subdirs = head + [None] + tail
        for name in subdirs:
            if name is None:
                group.append((None, None))
            else:
                assert(type(name) is str)
                path = os.path.join(directory, name)
                mode = os.lstat(path).st_mode
                if stat.S_ISDIR(mode):
                    compute(path, group, depth + 1)
                else:
                    group.append((name, mode))
        dir_name = os.path.basename(directory)
        data.append((dir_name, group))
    output = []
    compute(root, output, 0)
    return output


def compute_weights(root):
    if root is None:
        return 0
    weight = 1
    for node in root.children:
        weight += compute_weights(node)
    root.weight = weight
    return weight


def construct_tree(data):
    position = 0

    def construct(name, content, index, depth):
        nonlocal position
        node = Node(name)
        node.level = depth
        node.index = index
        node.position = position
        position += 1
        try:
            for i, (k, v) in enumerate(content):
                child = construct(k, v, i, depth + 1)
                child.parent = node
                node.children.append(child)
        except TypeError:
            node.mode = content
        return node
    root = construct(*data[0], 0, 0)
    compute_weights(root)
    return root


class Colorizer:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    _TEMPLATE = '\x1b[{}m'

    def __init__(self, enabled, bold):
        self.enabled = enabled
        self.bold = bold

    def colorize(self, text, color):
        if not self.enabled:
            return text
        beg = Colorizer._TEMPLATE.format(f'{"1;" * self.bold}{color}')
        end = Colorizer._TEMPLATE.format(0)
        return beg + text + end


class TreeView:
    def __init__(self, **kwargs):
        self.ch = BoxDrawingCharacters(kwargs.get('bold', False))
        self.width = kwargs.get('width', 2)
        self.indent = kwargs.get('indent', 1)

    def _padding(self):
        return ' ' * self.width

    def _hbar(self):
        return self.ch.hbar() * (self.width-1)

    def _make_name(self, node, is_last):
        def make(start, end):
            return start + self._hbar() + self.ch.ecap() + end
        if node.name:
            char = self.ch.bend() if is_last else self.ch.ltee()
            return make(char, node.name)
        if is_last:
            return make(self.ch.bend(), self.ch.hdots())
        else:
            return self.ch.vdots()

    def construct(self, root):
        queue = list(root.children)
        output = [' ' * self.indent] * root.weight
        output[0] += root.name
        while queue:
            node = queue.pop(0)
            is_last = node.index == len(node.parent.children) - 1
            output[node.position] += self._make_name(node, is_last)
            queue += node.children
            for i in range(1, node.weight):
                ch = ' ' if is_last else self.ch.vbar()
                output[node.position+i] += ch + self._padding()
        return '\n'.join(output)


def fatal(message):
    print(f'Error: {message}', file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Print a tree view of a directory.')
    parser.add_argument('-p', '--path', type=str, default='.', help='Path to a directory to view')
    parser.add_argument('-d', '--depth', type=int, default=8, help='Maximum tree depth displayed')
    parser.add_argument('-b', '--breadth', type=int, default=20,
                        help='Maximum number of entries to display in a given directory')
    parser.add_argument('-i', '--indent', type=int, default=1,
                        help='Number of whitespace characters preceeding the tree')
    parser.add_argument('-w', '--width', type=int, default=1,
                        help='Width of the connection from an entry to the tree trunk')
    parser.add_argument('-B', '--bold', action='store_true', default=False,
                        help='Use thicker box drawing characters for the tree')
    args = parser.parse_args(sys.argv[1:])

    bold = args.bold
    path = args.path
    if not os.path.isdir(path):
        fatal(f'path "{path}" must refer to a directory')

    def check_bounds(name, value, bounds):
        lower, upper = bounds
        if value not in range(lower, upper + 1):
            fatal(f'{name} "{value}" must be ∈ [{lower}, {upper}]')

    depth = args.depth
    check_bounds('depth', depth, (0, 15))

    breadth = args.breadth
    check_bounds('breadth', breadth, (0, 40))

    width = args.width
    check_bounds('width', width, (0, 80))

    indent = args.indent
    check_bounds('indent', indent, (0, 80))

    try:
        tree_data = compute_tree_data(path, depth, breadth)
        root = construct_tree(tree_data)
        view = TreeView(bold=bold, width=width, indent=indent)
        print(view.construct(root))
    except Exception as error:
        fatal(error)

if __name__ == '__main__':
    main()
