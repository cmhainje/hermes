# hermes

A Grade 34 Bureaucrat to help you create and manage repetitive, multi-file
tasks and experiments.

Hermes is a lightweight templating engine for _directories_. If you have a task
that involves copying whole directories, modifying a few lines in a few files,
and hitting `run`, Hermes can help automate this task and make sure you don't
miss anything.

Hermes can be useful for

- Cosmological simulations (that's what I'm using it for!)
- Machine learning experiments
- and more?

## Installation

Clone the repo, then `cd` into it and run

```bash
pip install -e .
```

(If `pip` complains that it can't find a "setup.py" file, try upgrading pip with
`pip install --upgrade pip`.)

This _should_ install `hermes` to your PATH. Try running

```bash
hermes --help
```

If the command `hermes` isn't found, though, you can alternatively try
`python -m hermes`.

## Usage

The basics:

1. Create a template directory.
2. Create a config file. (You can use `hermes config new` to make an empty one.) Fill it out with the parameters you want to use and tasks you might want to run.
3. `hermes create <new_dir>`.

### Template directory

The most important thing for `hermes` is the template directory. This is a
directory containing the files and folder structure you want for each copy that
will be made.

For example, if every experiment I run needs its own copy of a Python script,
"experiment.py", job scheduler submission script, "run.sh", my directory might
look like this:

```nolang
template/
  experiment.py
  run.sh
```

The version of experiment.py and run.sh that live here, however, are Jinja
templates. So, for example, `run.sh` might look like this:

```jinja
[run.sh]
#!/bin/bash
#SBATCH -J {{ name }}
#SBATCH -t 4:00:00

cd {{ directory }}
python experiment.py
```

And perhaps the Python script looks like this:

```jinja
[experiment.py]
print("{{ name }}")
print("{{ directory }}")
```

What Hermes can do is allow us to create new copies of this template directory, with
all the Jinja templates rendered using parameter values specified at the command
line.  So, for example, running `hermes create dir_name --name test` will copy
the entire directory tree of `template` into `./dir_name`. Then, all the Jinja
templates will be rendered with `directory` taking the value `/current/dir/dir_name`
(the value of `directory` gets expanded to an absolute path) and `name` taking the
value `test`; e.g. the results will look like:

```bash
[run.sh]
#!/bin/bash
#SBATCH -J test
#SBATCH -t 4:00:00

cd /current/dir/dir_name
python experiment.py
```

and

```python
[experiment.py]
print("test")
print("/current/dir/dir_name")
```

Note that template files are true Jinja templates; feel free to use any of Jinja's deeper functionality!

### Configuration

Before you can use `hermes`, you need to configure it. The configuration tells
Hermes

- the location of the template directory
- the names of the parameters that will be used in the Jinja templates
- the default values of these parameters
- what tasks can be executed

This is done with a JSON file called "hermes.json". An example file looks as
follows:

```json
{
    "template": "path/to/template",
    "parameters": {
        "name": "{{directory}}"
    },
    "tasks": {
        "greet": "echo Hello!"
    }
}
```

This file needs to live in one of the following places:

- locally: in your working directory or in one of its parent directories
- globally: `~/.config/hermes.json` for a global configuration (for example, if
Hermes only needs to be set up once per machine)

Both the local and global config files will be loaded, with local configuration
taking precedence over global configuration.

#### Config parameters

There are only a few protected parameter names:

- `"directory"`: this is a required parameter for `create` and `edit` actions
and, in all cases where Jinja templates are rendered, contains the path of the
directory being written to. It can be specified as a relative or absolute path,
but in all cases will be rendered as the full absolute path. If other parameters
shadow the value of `"directory"`, they will take its value as provided at the
command-line.
- `"template"`: this is generally specified by the config file (though it can be
manually specified for the `create` action), and contains the path to the
template directory. This can also be a relative or absolute path.
- `"multi"`: some actions (`create` in particular) use this to tell Hermes
whether a batch of simulations is being created all together

Otherwise, parameter names can be most anything that is acceptable for Python,
Jinja, and the command-line. Hyphens are problematic because they look like
subtraction to Python and Jinja, but underscores work.

The parameter values can also be most anything; because they will be input at
the command-line, they are _all_ interpreted as strings that are pasted as-is
into the template files. Note that you _can_ use Jinja filters to dynamically
adjust how variables are formatted. For example, parameter `"alpha": 20` could
be rendered as a float with format string ".3f" using Jinja filters:
`{{ "%.3f" % (alpha | float) }}`.  Alternatively,
you could just specify `--alpha "20.000"` for the same result.

Notice also that the default value of the parameter `"name"` looks like a Jinja
template variable! This syntax allows you to tell Hermes that the default value
of the `"name"` parameter should be the value of the `"directory"` parameter.
Note that _this_ does not use Jinja; the only valid use here is to specify
`"param_A": "{{ param_B }}"`, where `"param_B"` must also be a valid parameter.

### Actions

Hermes provides the following actions:

- `create`
- `edit`
- `copy`
- `clean`
- `run`

#### create

`hermes create` creates new copies of the template directory. It is invoked as
follows:

```bash
hermes create <directory> [--template] [--multi] [--params]
```

By default, the directory argument is required. The template argument is usually
filled by the value of `"template"` in the config file. `--multi` is a special
case that will be discussed below. `--params` is short-hand for _any_ parameters
specified in the config file.

#### edit

`hermes edit` allows you to modify the values of the parameters in your sim
after creation. It is invoked by:

```bash
hermes edit [directory] [--params]
```

The directory argument defaults to `"."`. The `--params` arguments are the
parameters you want to modify. Any other parameters are left unchanged.

Note that `edit` works by _patching_ your rendered template files to update the
specified parameters. It does _not_ re-render them from scratch. In particular,
this means that local modifications to the files will be preserved, as long as
they don't conflict with the patch itself.The patching is done using Google's
Diff-Match-Patch algorithms.

#### copy

`hermes copy` will copy an existing rendered directory to a new place and
automatically update the references to `directory` within. (You can also
overwrite the values of any of the parameters.) It is invoked by:

```bash
hermes copy <src> <dest> [--params]
```

This copies the rendered versions of the templates from `src` to `dest`. It does
_not_ copy any files or folders from `src` to `dest` that do not also exist in
the template directory.

`copy` also works by _patching_ the templates, not by re-rendering them. In
particular, this means that if `src` contains modified versions of the
templates, `dest` will have these modifications, too. However, the version in
`dest` will be patched so that any referecnes to `directory` correctly refer to
`dest`, not `src`. Other parameter overrides are handled in the same way as in
`edit`.

Note that parameters whose values defaulted to `directory` are not updated by
`copy`. For example, the parameter `name` in the example above. If a directory was
created by `hermes create A`, the parameter `name` takes the value `A`. Then,
running `hermes copy A B` will also have `name` taking the value `A` in the
directory `B`. To change this, just specify the new `name` manually:
`hermes copy A B --name B`.

Note that `copy` has alias `cp`.

#### clean

`hermes clean` deletes all files and folders in the directory that don't exist
in the template; e.g. it resets the directory. Note that it doesn't re-render
the Jinja templates, so any local modifications are left untouched. This action
is invoked as follows:

```bash
hermes clean [directory] [--multi]
```

The directory argument here is optional; it defaults to `"."`.

Note that `clean` has alias `rm`.

#### run

`hermes run` allows you to run pre-specified tasks inside of your rendered
directories. These tasks are configured in the `"tasks"` section of the config
file. It is invoked as follows:

```bash
hermes run <task> [directory] [--multi]
```

The task argument specifies the name of one of the tasks in the config file. The
directory argument gives the path to the directory in which to run the task; by
default, this is `"."`.

The tasks are simple shell commands. Hermes runs the commands from `directory`;
e.g. Hermes runs `cd {directory} && {command}`. The real advantage to using
these tasks, however, comes in combination with the `--multi` argument.

### Batched actions with the `--multi` argument

Several actions have an optional argument `--multi` that I've brushed past so
far. This argument allows you to use `hermes` to create and run tasks in
_batches_.

To use `--multi`, you need a CSV file containing the directory names and
parameters for a _batch_ of new directories you want to render. (It is
_required_ to contain a column named "directory".) Using our previous example of
just a "name" parameter, our CSV file might look like the following:

```csv
[params.csv]
directory,name
test_01,01
test_02,02
test_03,03
```

We can create _all_ of these at once with

```bash
hermes create --multi params.csv
```

Which results in copies of the template being rendered at `./test_01`,
`./test_02`, and `./test_03`. The result is _identical_ to if we had instead run

```bash
hermes create test_01 --name 01
hermes create test_02 --name 02
hermes create test_03 --name 03
```

(Note that when the `--multi` parameter is invoked, the `directory` parameter is
optional and defaults to `"."`. The directory parameter in this case specifies
the _parent_ directory for all the new rendered directories being created.)

Once a batch has been created with `--multi`, we can drop the path to the CSV
file, using just `--multi`. So, if we have created test_01, test_02, and test_03
using the `--multi` command, we can now run our task "greet" in each of these
directories using

```bash
hermes run greet --multi
```

Note that `--multi` has alias `-m`.

## Examples

The `examples/` directory contains some template directories and config files
that I have used.

### gml

The `gml` template is one that I've used for setting up cosmological large-scale
structure simulations. There are two codes used: monofonIC and Gadget4. Each of
these needs a parameter file and a SLURM job submission script. These all
contain filepaths that need to be correct. There is also a "name" parameter that
specifies the SLURM job name.

The config file contains two tasks: `make_ic` (which submits the monofonIC job)
and `submit` (which submits the Gadget4 job). Note that these are specified
relative to the root of the rendered directory, so running the
`run_monofonic.sh` script is done as `sbatch ics/run_monofonic.sh`, since the
script lives in a subdirectory called "ics".

There is also a sample "params.csv" file included for toying with the batched
actions.

Try it out for yourself! `cd` into `examples/gml`. Then try

```bash
$ hermes create test
Creating new simulation from template .../hermes/examples/gml/template in test.

$ cd test

$ hermes run greet
Running task 'greet' in ..
hello from .../hermes/examples/gml/test

$ head -n 3 sim/run_gadget.sh
#!/bin/bash
#SBATCH -J test_sim
#SBATCH -t 0-06:00:00

$ hermes edit --name asdf
Editing simulation in ..

$ head -n 3 sim/run_gadget.sh
#!/bin/bash
#SBATCH -J asdf_sim
#SBATCH -t 0-06:00:00
```

Or try out the batched actions!

```bash
$ hermes create multi_test -m params.csv
Running create on multiple simulations.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_1.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_2.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_3.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_4.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_5.
Creating new simulation from template .../hermes/examples/gml/template in multi_test/asdf_6.

$ cd multi_test

$ hermes run greet -m
Running run on multiple simulations.
Running task 'greet' in asdf_1.
hello from .../hermes/examples/gml/multi_test/asdf_1
Running task 'greet' in asdf_2.
hello from .../hermes/examples/gml/multi_test/asdf_2
Running task 'greet' in asdf_3.
hello from .../hermes/examples/gml/multi_test/asdf_3
Running task 'greet' in asdf_4.
hello from .../hermes/examples/gml/multi_test/asdf_4
Running task 'greet' in asdf_5.
hello from .../hermes/examples/gml/multi_test/asdf_5
Running task 'greet' in asdf_6.
hello from .../hermes/examples/gml/multi_test/asdf_6
```
