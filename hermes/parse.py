import logging

from argparse import ArgumentParser


def parse(cfg=None):
    logging.info("Setting up argument parser.")
    ap = ArgumentParser()

    subparsers = ap.add_subparsers(dest='action')

    # Create: create a new simulation
    create = subparsers.add_parser('create', help='creates a simulation')
    create.add_argument('directory', help='the name of the directory to create')
    create.add_argument('--template', help='template directory', default=None)

    # Edit: edit a simulation
    edit = subparsers.add_parser('edit', help='edits a simulation by re-rendering the templates with new values')
    edit.add_argument('directory', help='the directory to edit', nargs='?', default='.')

    # Clean: clean up a simulation
    clean = subparsers.add_parser('clean', help='cleans up a simulation', aliases=['rm'])
    clean.add_argument('directory', help='the directory or subdirectory to clean', nargs='?', default='.')

    # Copy: copy a simulation
    copy = subparsers.add_parser('copy', help='copies a simulation', aliases=['cp'])
    copy.add_argument('src', help='the source directory')
    copy.add_argument('dest', help='the destination directory')
    
    # Run: run a task
    run = subparsers.add_parser('run', help='runs a task')
    run.add_argument('task', help='the task to run')
    run.add_argument('directory', help='the directory to run the task in', nargs='?', default='.')

    # Config: create a new config file or show the current configuration
    config = subparsers.add_parser('config', help='manages the configuration')
    cfg_subs = config.add_subparsers(dest='config_action')
    cfg_new = cfg_subs.add_parser('new', help='creates a new configuration file')
    cfg_new.add_argument('directory', help='the directory to create the configuration file in', nargs='?', default='.')
    cfg_show = cfg_subs.add_parser('show', help='shows the current configuration')

    cfg_has_params = cfg is not None and 'parameters' in cfg and len(cfg['parameters']) > 0
    actions_with_params = ['create', 'edit', 'copy', 'cp']

    if cfg_has_params:
        logging.info("Adding parameters from config to relevant subparsers.")
        for param in cfg['parameters'].keys():
            logging.debug('Adding parameter "%s".', param)
            create.add_argument(f'--{param}', default=None)
            edit.add_argument(f'--{param}', default=None)
            copy.add_argument(f'--{param}', default=None)

    logging.info("Parsing arguments.")
    args = ap.parse_args()

    # if any parameters are specified to take the value of another parameters, update them here
    if cfg_has_params and args.action in actions_with_params:
        logging.info("Checking for parameters that are not set.")
        if args.action not in ['edit', 'copy', 'cp']:
            for param, value in cfg['parameters'].items():
                if getattr(args, param) is None:
                    setattr(args, param, value)

        logging.info("Checking for parameters that take the value of other parameters.")
        for param in cfg['parameters'].keys():
            value = getattr(args, param)
            if value.startswith('{{') and value.endswith('}}'):
                other_param = value[2:-2].strip()
                if not hasattr(args, other_param):
                    logging.warning('Parameter "%s" is set to take the value of "%s", but "%s" is not a parameter.', param, other_param, other_param)
                    continue

                logging.debug('Setting parameter "%s" to value of "%s" ("%s").', param, other_param, getattr(args, other_param))
                setattr(args, param, getattr(args, other_param))

    return args