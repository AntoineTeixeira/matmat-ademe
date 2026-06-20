#!/bin/bash

# Script to generate MatMat Python wheel

source env/bin/activate
python -m build --outdir build/
deactivate

