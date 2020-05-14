#!/bin/bash

# This is a script to help test this project's modules
# If you want to log all the outputs to file, try something like:
# ./modtests.sh 2>&1 | tee modtests.log
# And of course in this case the output will be BUFFERED
# Note that the path of log file should avoid pattern log/*.log
# Since this script will delete them during execution


# Wait for a newline before running every command
confirm=true

# Actual Bash binary file location
bash_bin=/bin/bash

# Main Python binary file location, CPython3 by default
main_bin=/usr/bin/python3

# Compare Python binary file location, PyPy3 by default
comp_bin=/usr/bin/pypy3

# Proxy binary file location, ProxyChains-NG 4 by default
proxy_bin=/usr/bin/proxychains4


# Check if a command exists
function cmd_exists() {
    [ -x $1 ] && return 0
    printf "\n\e[31mWARNING: COMMAND '$1' DOES NOT EXIST\e[0m\n\n"
    return 1
}

# Terminal this script if the command does not exist
function exist_or_exit() {
    cmd_exists $1 || exit
}

# Print and run a command
function print_and_run() {
    printf "\e[33m\$ $1\e[0m\n"
    $confirm && printf '(\e[32mENTER: Confirm\e[0m / \e[31m^C: Terminate\e[0m)'
    $confirm && read -p ' '
    echo
    $bash_bin -c "$1" || exit
    echo
}

# Show prettified module name line
function show_module_name() {
    sep==
    printf "$sep%.0s" {1..30}
    printf " $1 "
    printf "$sep%.0s" {1..30}
    echo
}


# Ensure the main python binary and bash binary exists
exist_or_exit $main_bin
exist_or_exit $bash_bin

# Add current directory location to Python's PATH
export PYTHONPATH=.


# Clear all logs before test starts
print_and_run 'rm log/*.log || true'

# Run tests of Timer module
show_module_name 'Timer Module Data Structure Test'
print_and_run "$main_bin timer/kheap.py"
print_and_run "$main_bin timer/rbtree.py"

show_module_name 'Timer Module Compared DST Test'
print_and_run "$main_bin timer/tests/dst.py"
cmd_exists $comp_bin && print_and_run "$comp_bin timer/tests/dst.py"

show_module_name 'Timer Module Function Test'
print_and_run "$main_bin timer/tests/func.py"

show_module_name 'Timer Module Compared Performance Test'
print_and_run "$main_bin timer/tests/perf.py"
cmd_exists $comp_bin && print_and_run "$comp_bin timer/tests/perf.py"

show_module_name 'Timer Module Main Timer Test'
print_and_run "$main_bin timer/main.py"


# Run tests of Server module
show_module_name 'Server Module Base Test'
print_and_run "$main_bin log/log.py"
print_and_run "$main_bin config/config.py"

# The output is large, so log to files instead
show_module_name 'Server Module StaticFile And FastCGIProxy Test'
print_and_run "$main_bin server/static_file.py > log/static.log"
print_and_run "$main_bin server/fastcgi_proxy.py > log/fastcgi.log"

# Test HTTP module with proxy if possible
show_module_name 'Server Module HTTPProxy Test'
http_bin=$main_bin
cmd_exists $proxy_bin && http_bin="$proxy_bin $http_bin"
print_and_run "$http_bin server/http_proxy.py > log/http.log"


# Show commands for manual testing of the rest modules
show_module_name 'To Be Manually Tested Modules'
echo "$main_bin worker/manager.py"


# Run the main server code and wait here
show_module_name 'Server Module Main Server Test'
echo 'Main Server Starting...'
echo 'You Should Be Able To Visit It With Your Broswer After It Started'
echo 'Send Ctrl+C To Exit Server During Testing'
print_and_run "$main_bin main.py"
