"""Defines a git hook to allow pre-commit warnings and errors about import order.

usage:
    exit_code = git_hook(strict=True|False, modify=True|False)
"""
import subprocess  # nosec - Needed for hook
from pathlib import Path
from typing import List

from isort import api


def get_output(command: List[str]) -> str:
    """
    Run a command and return raw output

    :param str command: the command to run
    :returns: the stdout output of the command
    """
    result = subprocess.run(command, stdout=subprocess.PIPE, check=True)  # nosec - trusted input
    return result.stdout.decode()


def get_lines(command: List[str]) -> List[str]:
    """
    Run a command and return lines of output

    :param str command: the command to run
    :returns: list of whitespace-stripped lines output by command
    """
    stdout = get_output(command)
    return [line.strip() for line in stdout.splitlines()]


def git_hook(strict: bool = False, modify: bool = False) -> int:
    """
    Git pre-commit hook to check staged files for isort errors

    :param bool strict - if True, return number of errors on exit,
        causing the hook to fail. If False, return zero so it will
        just act as a warning.
    :param bool modify - if True, fix the sources if they are not
        sorted properly. If False, only report result without
        modifying anything.

    :return number of errors if in strict mode, 0 otherwise.
    """

    # Get list of files modified and staged
    diff_cmd = ["git", "diff-index", "--cached", "--name-only", "--diff-filter=ACMRTUXB HEAD"]
    files_modified = get_lines(diff_cmd)

    errors = 0
    for filename in files_modified:
        if filename.endswith(".py"):
            # Get the staged contents of the file
            staged_cmd = ["git", "show", ":%s" % filename]
            staged_contents = get_output(staged_cmd)

            if not (
                api.sort_file(filename)
                if modify
                else api.check_code_string(staged_contents, file_path=Path(filename))
            ):
                errors += 1

    return errors if strict else 0
