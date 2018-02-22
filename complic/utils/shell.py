#!/usr/bin/env python

import logging
import subprocess
import shlex


def cmd(command, print_error=True):
    """Runs a subprocess command (without shell)."""
    logging.debug("Running: %s", command)

    # Avoid: TypeError: execve() ... must be encoded string without NULL
    if isinstance(command, unicode):
        command = command.encode('utf8')

    proc = subprocess.Popen(shlex.split(command),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if proc.returncode != 0 and print_error:
        logging.error("Something happened when running: %s", command)
        logging.error("STDOUT: %s", out.strip())
        logging.error("STDERR: %s", err.strip())
        logging.error("RC: %i", proc.returncode)

    return proc.returncode, out, err
