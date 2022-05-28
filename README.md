# treeview
A simple python script for displaying a filesystem hierarchy as a tree

## Example
This example displays the SQLite3 source tree.
`cd` into the directory containing `sqlite` and run

```bash
python3 treeview.py -n 10 ./sqlite
```

We see as our output:

```
sqlite
├╴LICENSE.md
├╴Makefile.in
├╴Makefile.linux-gcc
├╴Makefile.msc
├╴README.md
├╴VERSION
├╴aclocal.m4
├╴art
│ ├╴sqlite370.eps
│ ├╴sqlite370.ico
│ └╴sqlite370.jpg
├╴autoconf
│ ├╴INSTALL
│ ├╴Makefile.am
│ ├╴Makefile.fallback
│ ├╴Makefile.msc
│ ├╴README.first
│ ├╴README.txt
│ ├╴configure.ac
│ └╴tea
│   ├╴Makefile.in
│   ├╴README
│   ├╴aclocal.m4
│   ├╴configure.ac
│   ├╴doc
│   │ └╴sqlite3.n
│   ├╴license.terms
│   ├╴pkgIndex.tcl.in
│   ├╴tclconfig
│   │ ├╴install-sh
│   │ └╴tcl.m4
│   └╴win
│     ├╴makefile.vc
│     ├╴nmakehlp.c
│     └╴rules.vc
├╴config.guess
└╴<23 more...>
```

As shown above, the number of entries printed in each directory has been limited to 8 using the `-n` option.

Similarly, we can specify the number of levels to show using the `-L` option.
We write:

```bash
python3 treeview.py -n 10 -L 2 ./sqlite
```

This causes the first level to be printed:

```
sqlite
├╴LICENSE.md
├╴Makefile.in
├╴Makefile.linux-gcc
├╴Makefile.msc
├╴README.md
├╴VERSION
├╴aclocal.m4
├╴art
│ ├╴sqlite370.eps
│ ├╴sqlite370.ico
│ └╴sqlite370.jpg
├╴autoconf
│ ├╴INSTALL
│ ├╴Makefile.am
│ ├╴Makefile.fallback
│ ├╴Makefile.msc
│ ├╴README.first
│ ├╴README.txt
│ ├╴configure.ac
│ └╴tea
├╴config.guess
└╴<23 more...>
```

## Colorful Output
`treeview` to displaying the file and directory names in color.
This behavior can be suppressed by specifying an output file path, or by setting the `-c` flag.

## Tests
To run the tests, `cd` into `test` and run 

```bash
bash test.sh
```

The script will create an example directory tree and run `treeview` on it with different arguments, `diff`ing the results with hand-typed trees from the `answers` directory.
If a test fails, the location of the `diff` output will be reported.

## Contributing
There are a lot of cool features that could be added.
Feel free to create a pull request if you'd like to contribute.
