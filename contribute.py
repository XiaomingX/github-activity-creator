#!/usr/bin/env python
import argparse
import os
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    # Parse command-line arguments
    args = arguments(def_args)

    # Current date and default repository directory
    curr_date = datetime.now()
    directory = f'repository-{curr_date.strftime("%Y-%m-%d-%H-%M-%S")}'

    # Extract repository details from arguments
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email
    if repository:
        # Extract repository name from the provided repository URL
        start = repository.rfind('/') + 1
        end = repository.rfind('.')
        directory = repository[start:end]

    # Ensure days_before and days_after are not negative
    days_before = args.days_before
    days_after = args.days_after
    if days_before < 0 or days_after < 0:
        sys.exit('days_before and days_after must not be negative.')

    # Create and navigate to the repository directory
    os.mkdir(directory)
    os.chdir(directory)

    # Initialize a new Git repository
    run(['git', 'init', '-b', 'main'])

    # Set Git user details if provided
    if user_name:
        run(['git', 'config', 'user.name', user_name])
    if user_email:
        run(['git', 'config', 'user.email', user_email])

    # Calculate the start date for commits
    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days=days_before)

    # Loop through the date range to generate commits
    for day in (start_date + timedelta(n) for n in range(days_before + days_after)):
        # Skip weekends if --no_weekends is specified
        if args.no_weekends and day.weekday() >= 5:
            continue
        # Commit based on the specified frequency
        if randint(0, 100) < args.frequency:
            for commit_time in (day + timedelta(minutes=m) for m in range(contributions_per_day(args))):
                contribute(commit_time)

    # Push changes to remote repository if specified
    if repository:
        run(['git', 'remote', 'add', 'origin', repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('\nRepository generation completed successfully!')


def contribute(date):
    """Create a commit with a specific date."""
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', f'"{message(date)}"', '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    """Run a shell command and wait for it to complete."""
    Popen(commands).wait()


def message(date):
    """Generate a commit message based on the date."""
    return date.strftime('Contribution: %Y-%m-%d %H:%M')


def contributions_per_day(args):
    """Determine the number of commits per day."""
    max_c = min(max(args.max_commits, 1), 20)  # Limit commits per day to between 1 and 20
    return randint(1, max_c)


def arguments(argsval):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Automate Git commit generation.")
    parser.add_argument('-nw', '--no_weekends', action='store_true', default=False,
                        help="Avoid making commits on weekends.")
    parser.add_argument('-mc', '--max_commits', type=int, default=10,
                        help="Maximum commits per day (1-20). Default: 10.")
    parser.add_argument('-fr', '--frequency', type=int, default=80,
                        help="Percentage of days with commits (0-100). Default: 80.")
    parser.add_argument('-r', '--repository', type=str,
                        help="Remote repository URL (e.g., git@github.com:user/repo.git).")
    parser.add_argument('-un', '--user_name', type=str,
                        help="Override Git user.name.")
    parser.add_argument('-ue', '--user_email', type=str,
                        help="Override Git user.email.")
    parser.add_argument('-db', '--days_before', type=int, default=365,
                        help="Number of days before today to start committing. Default: 365.")
    parser.add_argument('-da', '--days_after', type=int, default=0,
                        help="Number of days after today to stop committing. Default: 0.")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
