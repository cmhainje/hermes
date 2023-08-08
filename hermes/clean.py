import logging

from os import remove, rmdir, walk
from os.path import join, relpath, abspath

from .usedvalues import load_used_values_from_parent


def walk_list(directory):
    dirs = []
    files = []
    for dirpath, dirnames, fnames in walk(directory):
        for dirname in dirnames:
            dirs.append(relpath(join(dirpath, dirname), directory))
        for fname in fnames:
            files.append(relpath(join(dirpath, fname), directory))

    return files, dirs


def clean(args):
    logging.info("Cleaning simulation in %s.", args.directory)

    used_values, simulation_dir = load_used_values_from_parent(args.directory)
    subdir_only = (simulation_dir != args.directory)

    template_dir = used_values['template']

    # Delete everything in args.directory that isn't in template_dir
    # (except for .hermes_usedvalues.json)
    template_files, template_dirs = walk_list(template_dir)
    simulation_files, simulation_dirs = walk_list(args.directory)

    if subdir_only:
        # fix paths
        fix_path = lambda path: relpath(abspath(join(args.directory, path)), simulation_dir) 
        simulation_files = [ fix_path(fname) for fname in simulation_files ]
        simulation_dirs = [ fix_path(dirname) for dirname in simulation_dirs ]

    for fname in simulation_files:
        if fname == '.hermes_usedvalues.json':
            continue
        if fname not in template_files:
            fullpath = join(simulation_dir, fname)
            remove(fullpath)
            logging.info("Deleted %s.", fullpath)

    for dirname in simulation_dirs[::-1]:
        if dirname not in template_dirs:
            fullpath = join(simulation_dir, dirname)
            rmdir(fullpath)
            logging.info("Deleted %s.", fullpath)

