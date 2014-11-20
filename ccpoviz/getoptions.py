"""
Geting the options for a particular plotting
============================================

This module contains driver functions that is able to get the options
dictionary for a particular run of the plotting.

"""

import json
import re

import pkg_resources

from .chainoptions import ChainOptions, UpdateError
from .util import terminate_program


def get_lines_sentinel(lines, beg_patt, end_patt):

    """Returns the lines based on the begining and end pattern

    :param lines: A list of strings for the lines
    :param beg_patt: A string giving the regular expression for the beginning
        pattern.
    :param end_patt: The end pattern
    :returns: A list of lines, beginning with the first line to match the
        beginning pattern and end with the line who matches the end pattern. An
        empty list if returned if the matching is not successful.

    """

    beg_re = re.compile(beg_patt)
    end_re = re.compile(end_patt)

    try:
        beg_pos = next(
            i for i, line in enumerate(lines) if beg_re.search(line)
            )
        end_pos = next(
            i for i, line in
            reversed(list(enumerate(lines))) if end_re.search(line)
            )
        if end_pos < beg_pos:
            raise StopIteration
    except StopIteration:
        return []

    return lines[beg_pos:end_pos + 1]


def get_options(mol_ops, mol, proj_ops):

    """Gets the options for this run

    This function will apply the molecular and project-level configurations to
    the default value to get the options for this run in the dictionary format.

    :param mol_ops: The options for the molecules, it can be string for the
        file name, or a string ``input-title`` to instruct the code to parse
        the tile section for the input. When that happend, the if the title
        contains a pair of matched ``---`` and ``...`` for a YAML document, it
        is going to be parsed as YAML, or the largest pair of curly brace are
        going to be parsed as JSON.
    :param mol: The molecule
    :param proj_ops: The file name for the project level configuration, if it
        ends with ``.yml`` or ``.yaml``, it is going to be parsed as YAML, or
        it is going to be parsed as JSON.

    """

    # pylint: disable=too-many-branches

    default = json.loads(
        pkg_resources.resource_string(__name__, 'data/defaultoptions.json')
        )

    config_dicts = []
    # Configuration dictionaries, starting with ones with higher priority

    if mol_ops == 'input-title':
        yaml_lines = get_lines_sentinel(
            mol.title, r'^ *--- *$', r'^ *\.\.\. *$'
            )
        if len(yaml_lines) != 0:
            import yaml
            try:
                mol_dict = yaml.load('\n'.join(yaml_lines))
            except yaml.parser.ParserError as err:
                terminate_program(
                    'Input title cannot be parsed as YAML.\n' +
                    ('%s' % err)
                    )
        else:
            json_lines = get_lines_sentinel(
                mol.title, r'^ *\{', r'\} *$'
                )
            if len(json_lines) != 0:
                try:
                    mol_dict = json.loads('\n'.join(json_lines))
                except ValueError as verr:
                    terminate_program(
                        'Input title cannot be parsed as JSON.\n' +
                        ('%s' % verr)
                        )
            else:
                terminate_program(
                    'The title of the input file cannot be '
                    'found to be JSON or YAML'
                    )
        config_dicts.append(mol_dict)
        config_files = [proj_ops, ]
    else:
        config_files = [mol_ops, proj_ops]

    for i in config_files:

        if i is None:
            continue

        try:
            file_obj = open(i, 'r')
        except IOError:
            terminate_program(
                'Cannot open the configuration file %s.' % i
                )
        content = file_obj.read()
        file_obj.close()

        if i.endswith(('.yml', '.yaml')):
            import yaml
            try:
                config_dicts.append(yaml.load(content))
            except yaml.parser.ParserError as err:
                terminate_program(
                    ('Configuration file %i cannot be parsed as YAML \n' % i)
                    + ('%s' % err)
                    )
        else:
            try:
                config_dicts.append(json.loads(content))
            except ValueError as err:
                terminate_program(
                    ('Configuration file %i cannot be parsed as JSON \n' % i)
                    + ('%s' % err)
                    )

    config_dicts.append(default)

    chainer = ChainOptions(default_coercion=True)
    try:
        return chainer.chain_options(*config_dicts)  # pylint: disable=star-args
    except UpdateError as err:
        terminate_program(
            'Invalid configuration: \n' +
            chainer.format_update_error(err)
            )
