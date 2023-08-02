import logging

from .config import load_configuration, create_config_file
from .create import create
from .parse import parse


logging.basicConfig(level=logging.DEBUG)


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

    
