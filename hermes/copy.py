import logging

from os.path import expanduser, abspath, join
from os import makedirs
from shutil import copyfile

from .clean import walk_list
from .render import find_templates
from .patch import patch
from .usedvalues import load_used_values, write_used_values


def copy(args):
    print("Copying simulation from %s to %s" % (args.src, args.dest))

    src = abspath(expanduser(args.src))
    dest = abspath(expanduser(args.dest))

    used_values = load_used_values(src)
    template_dir = abspath(expanduser(used_values["template"]))

    # remake the `template` directory structure in `dest`
    template_files, template_dirs = walk_list(template_dir)
    template_dirs = [dest] + template_dirs

    for dirname in template_dirs:
        makedirs(join(dest, dirname))
        logging.info("Made dir %s.", join(dest, dirname))

    # copy files in `template` from `src` to `dest`
    for fname in template_files:
        copyfile(join(src, fname), join(dest, fname))
        logging.info("Copied file from %s to %s.", join(src, fname), join(dest, fname))

    # find the files that look like Jinja templates
    jinja_templates = find_templates(template_dir)

    # now we use jinja to patch the templates
    jinja_params = dict((k, v) for k, v in used_values.items())
    new_values = ((k, v) for k, v in vars(args).items() if v is not None)
    jinja_params.update(new_values)
    jinja_params["directory"] = dest

    for template in jinja_templates:
        logging.info("Patching %s.", template)
        patch(template_dir, template, dest, used_values, jinja_params)

    # and finally we write out the values we used
    write_used_values(dest, jinja_params)
