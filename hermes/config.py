"""
config.py

look for and load config files
"""

import logging


def load_configuration():
    from pathlib import Path

    cfg = dict()

    # user global config
    global_file = Path("~/.config/hermes.json").expanduser()
    if global_file.is_file():
        logging.info("User global config found at %s.", global_file)
        cfg.update(load_config_file(global_file))
    else:
        logging.info("No user global config found.")

    # local config
    local_file = look_for_local_file()
    if local_file:
        logging.info("Local config found at %s.", local_file)
        cfg.update(load_config_file(local_file))
    else:
        logging.info("No local config found.")

    logging.debug("Configuration that was loaded: %s.", cfg)

    return cfg


def look_for_local_file(dir=None):
    from pathlib import Path

    if dir is None:
        dir = Path.cwd()
    else:
        dir = Path(dir)

    if dir.joinpath("hermes.json").is_file():
        return dir.joinpath("hermes.json")

    for parent in dir.parents:
        if parent.joinpath("hermes.json").is_file():
            return parent.joinpath("hermes.json")

    return None


def load_config_file(filepath):
    import json

    with open(filepath, "r") as f:
        config = json.load(f)

    return config


def create_config_file(directory):
    from os.path import join

    filename = join(directory, "hermes.json")
    logging.info("Creating new config file at %s.", filename)
    with open(filename, "w") as f:
        lines = [
            "{",
            '    "template": "default",',
            '    "parameters": {',
            "    },",
            '    "tasks": {',
            "    }",
            "}",
        ]
        f.write("\n".join(lines) + "\n")
