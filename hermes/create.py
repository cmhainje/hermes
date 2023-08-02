"""
create.py

create a new simulation
"""

import logging
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
    jinja_templates = []
    for dirpath, dirnames, fnames in walk(args.directory):
        for fname in fnames:
            fullpath = join(dirpath, fname)
            with open(fullpath, 'r') as f:
                contents = f.read()
                if JINJA_DELIMITER_REGEX.search(contents) is not None:
                    jinja_templates.append(relpath(fullpath, args.directory))
                    logging.debug("Found Jinja template %s.", fullpath)

    # now we use jinja to render the templates and replace the files
    jinja_params = vars(args)  # converts 'args' into a dict
    for template in jinja_templates:
        logging.info("Rendering template %s.", template)
        render_jinja_template(template, args.directory, jinja_params)


def render_jinja_template(template, directory, params):
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(directory))
    template = env.get_template(template)
    rendered = template.render(**params)

    with open(template.filename, 'w') as f:
        f.write(rendered)
