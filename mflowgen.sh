#!/bin/bash

# Upgrade pip
pip install -U pip

# Install Genesis2
if [ ! -d "Genesis2" ]; then
    git clone https://github.com/StanfordVLSI/Genesis2.git
    export GENESIS_HOME=$(realpath Genesis2/Genesis2Tools)
    export PERL5LIB="$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions:$PERL5LIB"
    export PATH="$GENESIS_HOME/bin:$GENESIS_HOME/gui/bin:$PATH"
    /bin/rm -rf "$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions/Compress"
fi

# Temporary fix for cvxpy
pip install cvxpy==1.1.7

# Install mflowgen
if [ ! -d "mflowgen" ]; then
    git clone https://github.com/cornell-brg/mflowgen
    cd mflowgen || exit
    pip install -e .
    cd ..
fi

# Install dragonphy
pip install -e .

# Make dependencies for design
python make.py --view asic

# Run mflowgen
mkdir -p build/mflowgen_dragonphy_top
cd build/mflowgen_dragonphy_top || exit
mflowgen run --design ../../designs/dragonphy_top
make synopsys-dc-synthesis
cd ../..
