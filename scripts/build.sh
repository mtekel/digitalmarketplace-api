#!/bin/bash
#
# Bootstrap virtualenv environment and postgres databases locally.
#
# NOTE: This script expects to be run from the project root with
# ./scripts/bootstrap.sh


# Install Python development dependencies
pip install -r requirements_for_test.txt

# Create Postgres databases
createdb digitalmarketplace
createdb digitalmarketplace_test

# Upgrade databases
python application.py db upgrade
