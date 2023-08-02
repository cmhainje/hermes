"""
edit.py

edit an existing simulation
"""

import logging

from .create import write_used_values
from .render import find_templates, render_jinja_template


def edit(args):
    import json

    from os.path import expanduser, join, abspath

    args.template = abspath(expanduser(args.template))
    args.directory = abspath(expanduser(args.directory))

    # find the simulation
    try:
        fname = join(args.directory, '.hermes_usedvalues.json')
        used_values = json.load(open(fname, 'r'))
    except OSError:
        logging.error("Could not find simulation at %s.\n(No .hermes_usedvalues.json file exists.)", args.directory)
        raise

    # replace any unspecified parameters with the values from the used values file
    for param, value in used_values.items():
        if getattr(args, param) is None:
            setattr(args, param, value)

    # find the files that look like Jinja templates
    jinja_templates = find_templates(args.template)

    # now we use jinja to re-render the templates and replace the files
    jinja_params = vars(args)  # converts 'args' into a dict
    for template in jinja_templates:
        logging.info("Rendering template %s.", template)
        render_jinja_template(args.template, template, args.directory, jinja_params)

    # and finally we write out the values we used
    write_used_values(args.directory, jinja_params)
