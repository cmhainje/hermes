import logging
import re


JINJA_DELIMITER_REGEX = re.compile(
    """
    \{                # opening curly brace
    (
        ( \{ .* \} )  # curly braces around _anything_
        |             # OR
        ( \% .* \% )  # percent signs around _anything_
    )
    \}                # closing curly brace
    """,
    re.VERBOSE
)


def looks_like_a_template(filepath):
    with open(filepath, 'r') as f:
        contents = f.read()
        return JINJA_DELIMITER_REGEX.search(contents) is not None


def find_templates(template_dir):
    from os import walk
    from os.path import join, expanduser, abspath, relpath

    template_dir = abspath(expanduser(template_dir))

    jinja_templates = []
    for dirpath, dirnames, fnames in walk(template_dir):
        for fname in fnames:
            fullpath = join(dirpath, fname)
            if looks_like_a_template(fullpath):
                jinja_templates.append(relpath(fullpath, template_dir))
                logging.debug("Found Jinja template %s.", fullpath)

    return jinja_templates


def render_jinja_template(template_dir, template_name, output_dir, params):
    from jinja2 import Environment, FileSystemLoader
    from os.path import join

    env = Environment(loader=FileSystemLoader(template_dir))
    rendered = env.get_template(template_name).render(**params)

    with open(join(output_dir, template_name), 'w') as f:
        f.write(rendered)


def render_template_only(template_dir, template_name, params):
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(template_dir))
    return env.get_template(template_name).render(**params)

