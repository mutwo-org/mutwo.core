#!/usr/bin/bash

# This script runs all tests in an adhoc created virtualenv.
TEST_VIRTUALENV_DIR=$(mktemp -d -t mutwo-test.XXXXXXX)
TEST_VIRTUALENV_NAME=$TEST_VIRTUALENV_DIR/mutwo_test_virtualenv
echo "Create test virtualenv in $TEST_VIRTUALENV_NAME"
pip3 install virtualenv
virtualenv $TEST_VIRTUALENV_NAME
source $TEST_VIRTUALENV_NAME/bin/activate
pip3 install .[testing]
cp -r tests $TEST_VIRTUALENV_DIR
cd $TEST_VIRTUALENV_DIR
nosetests --with-coverage --cover-package=mutwo
deactivate
