"""
edit.py

edit an existing simulation
"""

import logging

from .render import find_templates
from .usedvalues import load_used_values, write_used_values
from .patch import patch


def edit(args):
    from os.path import expanduser, abspath

    args.template = abspath(expanduser(args.template))
    args.directory = abspath(expanduser(args.directory))

    # replace any unspecified parameters with the values from the used values file
    used_values = load_used_values(args.directory)
    for param, value in used_values.items():
        if getattr(args, param) is None:
            setattr(args, param, value)

    # find the files that look like Jinja templates
    jinja_templates = find_templates(args.template)

    # now we use jinja to patch the templates
    jinja_params = vars(args)  # converts 'args' into a dict
    for template in jinja_templates:
        logging.info("Patching %s.", template)
        patch(args.template, template, args.directory, used_values, jinja_params)

    # and finally we write out the values we used
    write_used_values(args.directory, jinja_params)
