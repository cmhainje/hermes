from .diff_match_patch_lib import diff_match_patch
from .render import render_template_only
from os.path import join


def patch(template_dir, template_name, output_dir, used_values, new_values):
    dmp = diff_match_patch()

    old_render = render_template_only(template_dir, template_name, used_values)
    new_render = render_template_only(template_dir, template_name, new_values)

    diff = dmp.diff_main(old_render, new_render)
    dmp.diff_cleanupSemantic(diff)
    patches = dmp.patch_make(old_render, diff)

    existing_file = join(output_dir, template_name)
    with open(existing_file, "r") as f:
        current = f.read()

    patched, _ = dmp.patch_apply(patches, current)

    with open(existing_file, "w") as f:
        f.write(patched)
