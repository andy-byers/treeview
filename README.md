# treeview
A simple python script for displaying a filesystem hierarchy as a tree

## Example
This example displays the SQLite3 source tree.
`cd` into the directory containing `sqlite` and run

```bash
python3 treeview.py -n 8 ./sqlite
```

We see as our output:

```
sqlite
 ├╴Makefile.msc
 ├╴LICENSE.md
 ├╴install-sh
 ├╴configure.ac
 ├╴ltmain.sh
 ├╴test
 │ ├╴capi3c.test
 │ ├╴zipfile2.test
 │ ├╴orderby5.test
 │ ├╴tt3_vacuum.c
 │ ├╴fts3defer2.test
 │ ├╴e_changes.test
 │ ├╴conflict.test
 │ ├╴tkt-78e04e52ea.test
 │ └╴<1199 others...>
 ├╴configure
 ├╴art
 │ ├╴sqlite370.eps
 │ ├╴sqlite370.ico
 │ └╴sqlite370.jpg
 └╴<26 others...>
```

As shown above, the number of entries printed in each directory has been limited to 8 using the `-n` option.

Similarly, we can specify the number of levels to show using the `-L` option.
We write:

```bash
python3 treeview.py -n 8 -L 1 ./sqlite
```

This causes the first level to be printed:

```
sqlite
├╴Makefile.msc
├╴LICENSE.md
├╴install-sh
├╴configure.ac
├╴ltmain.sh
├╴test
├╴configure
├╴art
└╴<26 others...>
```

## Colorful Output
`treeview` defaults to displaying the file and directory names in color.
This behavior can be suppressed by specifying an output file path, or by setting the `-c` flag.

## Contributing
There are a lot of cool features that could be added.
Feel free to create a pull request if you'd like to contribute.
