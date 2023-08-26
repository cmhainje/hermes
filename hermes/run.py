import logging
import subprocess


def run(args, cfg):
    print("Running task '%s' in %s" % (args.task, args.directory))

    tasks = cfg["tasks"]
    if args.task not in tasks:
        logging.error("Task '%s' not found in config.", args.task)
        raise ValueError(f"Task '{args.task}' not found in config.")

    task = tasks[args.task]
    cmd = f"cd {args.directory} && {task}"
    logging.info("Running command %s.", cmd)
    subprocess.run(cmd, shell=True)
