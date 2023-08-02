"""
create.py

create a new simulation
"""

import logging

from .render import find_templates, render_jinja_template

import re


JINJA_DELIMITER_REGEX = re.compile("""
\{  # opening curly brace
(
    ( \{ .* \} )  # curly braces around _anything_
    |             # OR
    ( \% .* \% )  # percent signs around _anything_
)
\}  # closing curly brace""", re.VERBOSE)


def create(args):
    from os.path import expanduser, join, relpath, abspath
    from os import walk
    from shutil import copytree

    args.template = abspath(expanduser(args.template))
    args.directory = abspath(expanduser(args.directory))

    copytree(args.template, args.directory)
    logging.info("Copied template from %s to %s.", args.template, args.directory)

    # find the files that look like Jinja templates
    jinja_templates = find_templates(args.template)

    # now we use jinja to render the templates and replace the files
    jinja_params = vars(args)  # converts 'args' into a dict
    for template in jinja_templates:
        logging.info("Rendering template %s.", template)
        render_jinja_template(args.template, template, args.directory, jinja_params)

    # and finally we write out the values we used
    write_used_values(args.directory, jinja_params)


def write_used_values(directory, params):
    import json
    from os.path import join

    with open(join(directory, '.hermes_usedvalues.json'), 'w') as f:
        json.dump(params, f, indent=4, sort_keys=True)
        f.write('\n')
