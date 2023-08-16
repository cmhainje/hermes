import logging

from .clean import clean
from .config import load_configuration, create_config_file
from .copy import copy
from .create import create
from .edit import edit
from .parse import parse
from .run import run
from .multi import run_multi


logging.basicConfig(level=logging.WARNING)


def main():
    cfg = load_configuration()
    logging.debug("Configuration loaded: %s", cfg)

    args = parse(cfg)
    logging.debug("Arguments parsed: %s", args)

    if not hasattr(args, "template") or args.template is None:
        setattr(args, "template", cfg["template"])

    if args.action == "config":
        if args.config_action == "new":
            print("Creating new configuration file at %s" % args.directory)
            create_config_file(args.directory)
        elif args.config_action == "show":
            print("Printing current configuration")
            print(cfg)
        else:
            logging.error("Unknown config_action %s.", args.config_action)
            raise ValueError(f"Unknown config_action {args.config_action}.")
        return

    elif args.action == "create":
        run_multi(create, args)

    elif args.action == "edit":
        edit(args)

    elif args.action == "clean" or args.action == "rm":
        run_multi(clean, args)

    elif args.action == "copy" or args.action == "cp":
        copy(args)

    elif args.action == "run":
        run_multi(run, args, cfg)

    else:
        raise NotImplementedError(f"Action {args.action} not implemented.")
