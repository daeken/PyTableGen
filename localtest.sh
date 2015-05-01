#!/bin/bash

./build.sh
PYTHONPATH=`pwd` ./scripts/pytblgen $@