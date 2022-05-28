#!/usr/bin/env bash

SELF_DIR=$(pwd)
ROOT_DIR=$(dirname "$SELF_DIR")
TARGET="$ROOT_DIR/treeview.py"
OUTPUT="$SELF_DIR/output.txt"
TREE="$SELF_DIR/tree"
EMPTY="$SELF_DIR/empty"

DIFF_PREFIX='/tmp/treeview_diff_'
FAIL_START="$(tput setaf 1)$(tput bold)[FAIL]$(tput setaf 7):"
PASS_START="$(tput setaf 2)$(tput bold)[PASS]$(tput setaf 7):"
LABEL_END=$(tput sgr 0)

declare -A ANSWERS
ANSWERS['ascii_only']='answers/ascii_only.txt'
ANSWERS['default_parameters']='answers/default_parameters.txt'
ANSWERS['directories_only']='answers/directories_only.txt'
ANSWERS['empty_directory']='answers/empty_directory.txt'
ANSWERS['indentation']='answers/indentation.txt'
ANSWERS['show_hidden']='answers/show_hidden.txt'
ANSWERS['with_limit']='answers/with_limit.txt'
ANSWERS['with_max_depth']='answers/with_max_depth.txt'

treeview () {
  python3 "$TARGET" -o "$OUTPUT" "$*" "$TREE"
}

validate() {
  local BASENAME=$(basename "$1")
  local DIFF_OUT="$DIFF_PREFIX$BASENAME"
  if ! diff "$OUTPUT" "$1" > "$DIFF_OUT"; then
    echo "$FAIL_START $BASENAME${LABEL_END}: Check $DIFF_OUT for the diff"
  else
    echo "$PASS_START $BASENAME${LABEL_END}"
  fi
}

reset() {
  true > "$OUTPUT"
}

if [ ! -d "$EMPTY" ]; then
  mkdir "$EMPTY"
fi

if [ ! -d "$TREE" ]; then
    mkdir "$TREE"
    mkdir "$TREE/a"
    mkdir "$TREE/a/b"
    mkdir "$TREE/a/b/c"
    mkdir "$TREE/a/b/c/d"
    mkdir "$TREE/a/b/c/d/e"
    mkdir "$TREE/a/b/c/d/e/f"
    mkdir "$TREE/a/b/c/d/e/f/g"
    mkdir "$TREE/a/b/c/d/e/f/h"
    mkdir "$TREE/a/b/c/d/i"
    mkdir "$TREE/a/b/j"
    mkdir "$TREE/a/k"
    mkdir "$TREE/a/k/l"
    mkdir "$TREE/a/k/l/m"
    mkdir "$TREE/a/n"
    mkdir "$TREE/a/o"
    touch "$TREE/a/1"
    touch "$TREE/a/2"
    touch "$TREE/a/b/3"
    touch "$TREE/a/b/c/d/e/f/4"
    touch "$TREE/a/b/c/d/e/f/5"
    touch "$TREE/a/b/c/d/e/f/g/6"
    touch "$TREE/a/k/l/7"
    touch "$TREE/a/k/l/8"
    touch "$TREE/a/.A"
    touch "$TREE/a/b/.B"
    touch "$TREE/a/b/c/.C"
    touch "$TREE/a/b/c/d/e/f/.F"
    touch "$TREE/a/b/c/d/i/.I"
    touch "$TREE/a/k/l/.L"
fi

reset
python3 "$TARGET" -o "$OUTPUT" "$EMPTY"
validate ${ANSWERS['empty_directory']}

reset
python3 "$TARGET" -o "$OUTPUT" "$TREE"
validate ${ANSWERS['default_parameters']}

reset
treeview '-A'
validate ${ANSWERS['ascii_only']}

reset
treeview '-a'
validate ${ANSWERS['show_hidden']}

reset
treeview '-d'
validate ${ANSWERS['directories_only']}

reset
treeview '-I 4'
validate ${ANSWERS['indentation']}

reset
treeview '-n 3'
validate ${ANSWERS['with_limit']}

reset
treeview '-L 3'
validate ${ANSWERS['with_max_depth']}


