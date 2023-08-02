import logging

from .usedvalues import load_used_values, write_used_values
from .render import find_templates, render_jinja_template

def copy(args):
    from os.path import expanduser, abspath
    from shutil import copytree

    src = abspath(expanduser(args.src))
    used_values = load_used_values(src)

    dest = abspath(expanduser(args.dest))
    
    # copy the template directory
    copytree(used_values['template'], dest)
    logging.info("Copied template from %s to %s.", used_values['template'], dest)

    # find the files that look like Jinja templates
    jinja_templates = find_templates(used_values['template'])

    # now we use jinja to render the templates and replace the files
    jinja_params = used_values  # converts 'args' into a dict
    jinja_params['directory'] = dest

    for template in jinja_templates:
        logging.info("Rendering template %s.", template)
        render_jinja_template(used_values['template'], template, dest, jinja_params)

    # and finally we write out the values we used
    write_used_values(dest, jinja_params)





