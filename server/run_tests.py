#!/usr/bin/env python
import subprocess
import sys
import argparse

def run_tests(test_type=None, verbose=False, coverage=False):
    """Run the specified tests with optional coverage report."""
    command = ['pytest']
    
    if verbose:
        command.append('-v')
        
    if coverage:
        command.extend(['--cov=app', '--cov-report=term-missing'])
    
    if test_type:
        if test_type == 'unit':
            command.append('tests/unit')
        elif test_type == 'service':
            command.append('tests/service')
        elif test_type == 'repo':
            command.append('tests/repo')
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tests with optional coverage report.')
    parser.add_argument('--type', choices=['unit', 'integration', 'functional'],
                      help='Type of tests to run')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Verbose output')
    parser.add_argument('--coverage', action='store_true',
                      help='Generate coverage report')
    
    args = parser.parse_args()
    run_tests(args.type, args.verbose, args.coverage)