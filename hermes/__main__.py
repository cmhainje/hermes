import logging

from argparse import ArgumentParser

from .config import load_configuration, create_config_file
from .create import create


logging.basicConfig(level=logging.DEBUG)


def parse(cfg=None):
    logging.info("Setting up argument parser.")
    ap = ArgumentParser()

    subparsers = ap.add_subparsers(dest='action')

    # Create: create a new simulation
    create = subparsers.add_parser('create', help='creates a simulation')
    create.add_argument('directory', help='the directory to create the simulation in', nargs='?', default='.')
    create.add_argument('--template', help='template directory', default=None)

    # Clean: clean up a simulation
    clean = subparsers.add_parser('clean', help='cleans up a simulation')
    clean.add_argument('directory', help='the directory to clean', nargs='?', default='.')
    clean.add_argument('--template', help='template directory', default=None)

    # Config: create a new config file or show the current configuration
    config = subparsers.add_parser('config', help='manages the configuration')
    cfg_subs = config.add_subparsers(dest='config_action')
    cfg_new = cfg_subs.add_parser('new', help='creates a new configuration file')
    cfg_new.add_argument('directory', help='the directory to create the configuration file in', nargs='?', default='.')
    cfg_show = cfg_subs.add_parser('show', help='shows the current configuration')

    if cfg is not None and 'parameters' in cfg and len(cfg['parameters']) > 0:
        logging.info("Adding parameters from config to argument parser.")
        for param, default in cfg['parameters'].items():
            logging.debug('Adding parameter "%s" with default "%s".', param, default)
            ap.add_argument(f'--{param}', default=default)

    logging.info("Parsing arguments.")
    args = ap.parse_args()

    # if any parameters are specified to take the value of another parameters, update them here
    if cfg is not None and 'parameters' in cfg and len(cfg['parameters']) > 0:
        logging.info("Checking for parameters that take the value of other parameters.")

        for param in cfg['parameters'].keys():
            value = getattr(args, param)
            if value.startswith('{{') and value.endswith('}}'):
                other_param = value[2:-2]
                if not hasattr(args, other_param):
                    logging.warning('Parameter "%s" is set to take the value of "%s", but "%s" is not a parameter.', param, other_param, other_param)
                    continue

                logging.debug('Setting parameter "%s" to value of "%s" ("%s").', param, other_param, getattr(args, other_param))
                setattr(args, param, getattr(args, other_param))

    return args


def main():
    cfg = load_configuration()
    logging.debug("Configuration loaded: %s", cfg)

    args = parse(cfg)
    logging.debug("Arguments parsed: %s", args)

    if args.action == 'config':
        if args.config_action == 'new':
            logging.info("Creating new configuration file at %s.", args.directory)
            create_config_file(args.directory)
        elif args.config_action == 'show':
            logging.info("Printing current configuration.")
            print(cfg)
        else:
            logging.error("Unknown config_action %s.", args.config_action)
            raise ValueError(f"Unknown config_action {args.config_action}.")
        return

    if args.template is None:
        args.template = cfg['template']

    if args.action == 'create':
        print("args.action is create!")
        create(args)

    
