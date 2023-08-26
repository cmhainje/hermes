import logging
import csv

from os.path import join


MULTI_FILE = ".hermes_multi.json"


def read_multi_parameter(multi):
    from os.path import isdir, join

    # multi might be a csv file
    if multi.lower().endswith(".csv"):
        return {"directories": read_csv(multi)}

    # multi might be a directory
    elif isdir(multi):
        return read_used_values(multi)

    else:
        logging.error("Could not read multi parameter %s.", multi)
        raise ValueError(f"Could not read multi parameter {multi}.")


class FakeArgs:
    def __init__(self, params):
        for k, v in params.items():
            setattr(self, k, v)


def run_multi(action_fn, args, *extra_args):
    if hasattr(args, "multi") and args.multi is not None:
        print("Running %s on multiple simulations" % args.action)
        params = read_multi_parameter(args.multi)

        if "template" not in params:
            params["template"] = args.template

        for p in params["directories"]:
            logging.info("Running %s on simulation %s.", args.action, p["directory"])
            fake_args = FakeArgs(p)
            setattr(fake_args, "template", args.template)
            if hasattr(args, "task"):
                setattr(fake_args, "task", args.task)
            if (
                not fake_args.directory.startswith("/")
                and args.directory is not None
                and args.directory != "."
            ):
                setattr(
                    fake_args, "directory", join(args.directory, fake_args.directory)
                )
            action_fn(fake_args, *extra_args)

        write_used_values(args.directory, params)

    else:
        action_fn(args, *extra_args)


def read_csv(filename):
    logging.info("Reading CSV file %s.", filename)
    with open(filename, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_used_values(directory, multi_params):
    import json
    from os.path import join

    with open(join(directory, MULTI_FILE), "w") as f:
        json.dump(multi_params, f, indent=4, sort_keys=True)
        f.write("\n")


def read_used_values(directory):
    import json
    from os.path import join

    fname = join(directory, MULTI_FILE)
    logging.info("Reading parameters from %s.", fname)

    try:
        return json.load(open(fname, "r"))
    except OSError:
        logging.error(
            "Could not find multi simulation at %s.\n(No %s file exists.)",
            directory,
            MULTI_FILE,
        )
        raise
