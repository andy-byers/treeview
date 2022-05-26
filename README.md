# treeview
A simple python script for displaying a filesystem hierarchy as a tree

## Example
This example displays the SQLite3 source tree. 
`cd` into the directory containing `sqlite` and run

```bash
python3 treeview.py -p ./sqlite -b 8 -B
```

The `-b` option specifies the maximum "breadth", that is, the maximum number of entries to display in each directory.
This option is useful for preventing enormous trees from being printed in large directories.
Also see `-d` which specifies the maximum depth.
The `-B` option causes thicker box drawing characters to be used.
 
We see as our output:

```
sqlite
 ┣╸Makefile.msc
 ┣╸LICENSE.md
 ┣╸install-sh
 ┣╸configure.ac
 ┣╸ltmain.sh
 ┣╸test
 ┃ ┣╸capi3c.test
 ┃ ┣╸zipfile2.test
 ┃ ┣╸orderby5.test
 ┃ ┣╸tt3_vacuum.c
 ┃ ┣╸fts3defer2.test
 ┃ ┣╸e_changes.test
 ┃ ┣╸conflict.test
 ┃ ⁞
 ┃ ┗╸interrupt2.test
 ┣╸configure
 ⁞
 ┗╸src
   ┣╸test_init.c
   ┣╸json.c
   ┣╸printf.c
   ┣╸btree.c
   ┣╸test_multiplex.c
   ┣╸dbstat.c
   ┣╸test_func.c
   ⁞
   ┗╸test_syscall.c
```

The vertical ellipsis, `⁞`, indicate that entries have been removed due to the maximum breadth being exceeded.
See what happens when we set the maximum depth to 0. We write:

```bash
python3 treeview.py -p ./sqlite -b 8 -d 0 -B
```

The maximum depth refers to the deepest level that will be displayed, starting at 0 in the target directory.
This causes just 8 entries in the target directory to be printed:

```
 sqlite
 ┣╸Makefile.msc
 ┣╸LICENSE.md
 ┣╸install-sh
 ┣╸configure.ac
 ┣╸ltmain.sh
 ┣╸test
 ┃ ┗╸⋯
 ┣╸configure
 ⁞
 ┗╸src
```

## Contributing
There are a lot of cool features that could be added.
Feel free to create a pull request if you'd like to contribute.
