#!/bin/env python

import os
import argparse
import subprocess
from pathlib import Path

project_root = Path(__file__).parent
os.chdir(project_root)

parser = argparse.ArgumentParser(description="Setup the project")
parser.add_argument("llvm_config", type=str, help="Path to llvm-config")
args = parser.parse_args()

llvm_config = args.llvm_config


def call_llvm_config(args):
    return subprocess.check_output([llvm_config] + args).decode("utf-8").strip()


def llvm_config_return_code(args):
    return subprocess.call([llvm_config] + args)


llvm_version = call_llvm_config(["--version"]).strip().split(".")[0]
expected_version = (project_root / "VERSION").read_text().strip().split(".")[0]
if llvm_version != expected_version:
    print("LLVM version mismatch. Exiting...")
    print(
        f"Expected LLVM version {expected_version} from project config, got {llvm_version}"
    )
    exit(2)


default_mode = None
support_static_mode = False
support_shared_mode = False
if llvm_config_return_code(["--link-static", "--libs"]) == 0:
    default_mode = "static"
    support_static_mode = True
if llvm_config_return_code(["--link-shared", "--libs"]) == 0:
    default_mode = "shared"
    support_shared_mode = True

if default_mode is None:
    print(
        "llvm-config can't determine a linking mode, both --link-static and \
        --link-shared failed. Exiting..."
    )
    exit(3)

base_cflags = call_llvm_config(["--cflags"]).split()
ldflags = call_llvm_config(["--ldflags"]).split() + ["-lstdc++"]
llvm_targets = call_llvm_config(["--targets-built"]).split()

# rm -rf src
# cp -r llvm-project/llvm/bindings/ocaml src
src_path = project_root / "src"
if src_path.exists():
    subprocess.run(["rm", "-rf", str(src_path)])
subprocess.run(
    [
        "cp",
        "-r",
        str(project_root / "llvm-project/llvm/bindings/ocaml"),
        str(src_path),
    ]
)


def replace_target_with_components(in_file: Path, out_file: Path, components: str):
    with in_file.open() as f:
        content = f.read()
    content = content.replace("@TARGET@", components)
    with out_file.open("w") as f:
        f.write(content)


def mk_backend_sources(target: str):
    base_dir = project_root / "src" / "backend" / target
    base_dir.mkdir(parents=True, exist_ok=True)
    # TODO


# TODO: copy setup.sh's create_dune_file function here
