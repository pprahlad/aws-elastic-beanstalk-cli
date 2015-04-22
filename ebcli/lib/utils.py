# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import datetime
import logging
import os
import platform
import re
import subprocess
import sys
import warnings

from botocore.compat import six
from cement.utils.misc import minimal_logger
from six.moves import urllib
from subprocess import Popen, PIPE, STDOUT

from ..objects.exceptions import CommandError
from ..core import io, fileoperations


LOG = minimal_logger(__name__)


def prompt_for_item_in_list(lst, default=1):
    ind = prompt_for_index_in_list(lst, default)
    return lst[ind]


def prompt_for_index_in_list(lst, default=1):
    for x in range(0, len(lst)):
        io.echo(str(x + 1) + ')', lst[x])

    while True:
        try:
            choice = int(io.prompt('default is ' + str(default),
                                   default=default))
            if not (0 < choice <= len(lst)):
                raise ValueError  # Also thrown by non int numbers
            else:
                break
        except ValueError:
            io.echo('Sorry, that is not a valid choice. '
                    'Please choose a number between 1 and ' +
                    str(len(lst)) + '.')
    return choice - 1


def get_unique_name(name, current_uniques):
    # with warnings.catch_warnings():
    #     warnings.simplefilter('ignore')
    #     if sys.version_info[0] >= 3:
    #         base_name = name
    #     else:
    #         base_name = name.decode('utf8')
    base_name = name

    number = 2
    while base_name in current_uniques:
        base_name = name + str(number)
        number += 1

    return base_name


def mask_vars(key, value):
    if (re.match('.*_CONNECTION_STRING', key) or
                key == 'AWS_ACCESS_KEY_ID' or
                key == 'AWS_SECRET_KEY') \
        and value is not None:
            value = "*****"

    return key, value


def print_list_in_columns(lst):
    """
    This function is currently only intended for environmant names,
    which are guaranteed to be 23 characters or less.
    :param lst: List of env names
    """
    if sys.stdout.isatty():
        lst = list_to_columns(lst)
        index = 0
        for x in range(0, len(lst[0])):
            line = []
            for i in range(0, len(lst)):
                try:
                    line.append(lst[i][x])
                except IndexError:
                    pass

            io.echo_and_justify(25, *line)
    else:
        # Dont print in columns if using pipe
        for i in lst:
            io.echo(i)


def list_to_columns(lst):
    COLUMN_NUM = 3
    assert len(lst) > COLUMN_NUM, "List size must be greater than {0}".\
        format(COLUMN_NUM)
    remainder = len(lst) % COLUMN_NUM
    column_size = len(lst) // COLUMN_NUM
    if remainder != 0:
        column_size += 1
    colunms = [[] for i in range(0, COLUMN_NUM)]
    index = 0
    stop = column_size
    for x in range(0, COLUMN_NUM):
        colunms[x] += lst[index:stop]
        index = stop
        stop += column_size
    return colunms


def url_encode(data):
    return urllib.parse.quote(data)


def is_ssh():
    return "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate


def exec_cmd(args, live_output=True):
    """
    Execute a child program (args) in a new process. Displays
    live output by default.
    :param args: list: describes the command to be run
    :param live_output: bool: whether to print live output
    :return str: child program output
    """

    LOG.debug(' '.join(args))

    process = Popen(args, stdout=PIPE, stderr=STDOUT)
    output = []

    for line in iter(process.stdout.readline, b''):
        line = line.decode('utf-8')
        if line != os.linesep:
            if live_output:
                sys.stdout.write(line)
                sys.stdout.flush()
            else:
                LOG.debug(line)

        output.append(line)

    process.stdout.close()
    process.wait()


    returncode = process.returncode
    error_msg = 'Exited with return code {}'.format(returncode)
    output_str = ''.join(output)

    if returncode:
        raise CommandError(error_msg, output_str, returncode)
    return output_str


exec_cmd_live_output = exec_cmd


def exec_cmd_quiet(args):
    return exec_cmd(args, False)


def flatten(lists):
    """
    Return a new (shallow) flattened list.
    :param lists: list: a list of lists
    :return list
    """

    return [item for sublist in lists for item in sublist]


def anykey(d):
    """
    Return any key in dictionary.
    :param d: dict: dictionary
    :return object
    """
    return next(six.iterkeys(d))


def last_modified_file(filepaths):
    """
    Return the most recently modified file.
    :param filepaths: list: paths to files
    :return str
    """

    return max(filepaths, key=os.path.getmtime)


def get_data_from_url(url, timeout=20):
    return urllib.request.urlopen(url, timeout=timeout).read()


def print_from_url(url):
    result = get_data_from_url(url)
    io.echo(result)


def save_file_from_url(url, location, filename):
    result = get_data_from_url(url)

    return fileoperations.save_to_file(result, location, filename)


# http://stackoverflow.com/a/5164027
def prettydate(d):
    if isinstance(d, float):  # epoch timestamp
        d = datetime.datetime.utcfromtimestamp(d)

    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s // 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s // 3600)
