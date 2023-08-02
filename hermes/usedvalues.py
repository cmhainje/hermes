import logging

def write_used_values(directory, params):
    import json
    from os.path import join

    with open(join(directory, '.hermes_usedvalues.json'), 'w') as f:
        json.dump(params, f, indent=4, sort_keys=True)
        f.write('\n')


def read_used_values(directory):
    import json
    from os.path import join

    try:
        fname = join(directory, '.hermes_usedvalues.json')
        return json.load(open(fname, 'r'))
    except OSError:
        logging.error("Could not find simulation at %s.\n(No .hermes_usedvalues.json file exists.)", directory)
        raise
