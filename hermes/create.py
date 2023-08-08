"""
create.py

create a new simulation
"""

import logging

from os.path import expanduser, abspath
from shutil import copytree

from .render import find_templates, render_jinja_template
from .usedvalues import write_used_values


def create(args):
    print(
        "Creating new simulation from template %s in %s."
        % (args.template, args.directory)
    )

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
