import sys
import os
import subprocess
import yaml

usage = f"Usage: python3 {sys.argv[0]} (setup|build) <config.yml>"


def run_process(*commands, setup_cmd=None, cwd=None, may_fail=False):
    cmd = ""
    if setup_cmd is not None:
        cmd += f"{setup_cmd} && "
    cmd += " ".join(commands)

    rc = subprocess.call(cmd, cwd=cwd, shell=True)

    if rc != 0 and not may_fail:
        print("Error running command:", cmd)
        sys.exit(1)


def load_config(*required_keys):
    required_keys = set(required_keys)
    if len(sys.argv) < 3:
        print(usage)
        sys.exit(1)

    with open(sys.argv[2], "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if not required_keys.issubset(config.keys()):
        print("Missing keys in config file", required_keys - config.keys())
        sys.exit(1)

    for key in required_keys:
        if config[key] is None:
            config[key] = ""

    class Config:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    return Config(**config)


def reset_branch(branch=None, *, cwd=None):
    if branch is not None:
        run_process("git checkout", branch, cwd=cwd)
    run_process("git fetch", cwd=cwd)
    run_process("git reset --hard", cwd=cwd)
    run_process("git clean -xfd", cwd=cwd)


def setup():
    cfg = load_config(
        "checkout_dir",
        "upstream_repo",
        "upstream_ref",
        "downstream_repo",
        "downstream_feature_branches",
    )

    upstream_remote = "autosetup_upstream"
    upstream_base_branch = f"autosetup_main"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    patches_dir = os.path.join(script_dir, "patches")

    cfg.checkout_dir = os.path.abspath(cfg.checkout_dir)

    upstream_url = f"https://github.com/{cfg.upstream_repo}.git"
    downstream_url = f"https://github.com/{cfg.downstream_repo}.git"

    if cfg.upstream_ref.startswith("tag:"):
        checkout_ref = f"refs/rtags/{upstream_remote}/{cfg.upstream_ref[4:]}"
    else:
        checkout_ref = f"{upstream_remote}/{cfg.upstream_ref}"

    downstream_feature_branches = [
        branch
        for branch in cfg.downstream_feature_branches.split(";")
        if len(branch) > 0
    ]

    run_process("git config --global --add safe.directory", cfg.checkout_dir)
    run_process("git config --global user.email autobuild", cfg.checkout_dir)
    run_process("git config --global user.name autobuild", cfg.checkout_dir)

    # Get repo in as-new state
    if not os.path.exists(cfg.checkout_dir):
        run_process("git clone", downstream_url, cfg.checkout_dir)
    else:
        reset_branch(cwd=cfg.checkout_dir)
        for branch in downstream_feature_branches:
            reset_branch(branch, cwd=cfg.checkout_dir)

    # Load upstream data
    run_process(
        "git remote add",
        upstream_remote,
        upstream_url,
        cwd=cfg.checkout_dir,
        may_fail=True,
    )
    run_process(
        f"git fetch {upstream_remote} --no-tags +refs/tags/*:refs/rtags/{upstream_remote}/*",
        cwd=cfg.checkout_dir,
    )

    # Checkout requested ref
    run_process(
        "git checkout",
        checkout_ref,
        cwd=cfg.checkout_dir,
    )

    # Create base branch
    run_process(
        "git branch -D",
        upstream_base_branch,
        cwd=cfg.checkout_dir,
        may_fail=True,
    )
    run_process(
        "git switch -c",
        upstream_base_branch,
        cwd=cfg.checkout_dir,
    )

    # Apply patches
    for patch in os.listdir(patches_dir):
        patch_file = os.path.join(patches_dir, patch)
        run_process(f"git apply {patch_file}", cwd=cfg.checkout_dir)

    # Commit patches
    run_process("git add .", cwd=cfg.checkout_dir)
    run_process("git commit -m Patches", cwd=cfg.checkout_dir)

    # Rebase feature branches on top of main
    base_branch = upstream_base_branch
    for branch in downstream_feature_branches:
        run_process("git checkout", branch, cwd=cfg.checkout_dir)
        run_process("git rebase", base_branch, cwd=cfg.checkout_dir)
        base_branch = branch


def build():

    cfg = load_config(
        "checkout_dir",
        "build_dir",
        "build_dep_dir",
        "install_dir",
        "build_type",
        "cmake_flags",
        "environment_cmd",
    )

    cfg.environment_cmd = cfg.environment_cmd if len(cfg.environment_cmd) > 0 else None

    cfg.checkout_dir = os.path.abspath(cfg.checkout_dir)
    cfg.build_dir = os.path.abspath(cfg.build_dir)
    cfg.build_dep_dir = os.path.abspath(cfg.build_dep_dir)
    cfg.install_dir = os.path.abspath(cfg.install_dir)

    cmake_flags = f"-DCMAKE_BUILD_TYPE={cfg.build_type} {cfg.cmake_flags}"

    run_process(
        f"cmake -S {cfg.checkout_dir}/deps -B {cfg.build_dep_dir}",
        cmake_flags,
        setup_cmd=cfg.environment_cmd,
    )

    run_process(
        f"cmake --build {cfg.build_dep_dir} --config {cfg.build_type}",
        setup_cmd=cfg.environment_cmd,
    )

    run_process(
        f"cmake -S {cfg.checkout_dir} -B {cfg.build_dir}",
        f"-DCMAKE_PREFIX_PATH={cfg.build_dep_dir}/destdir/usr/local",
        f"-DCMAKE_INSTALL_PREFIX={cfg.install_dir}",
        cmake_flags,
        setup_cmd=cfg.environment_cmd,
    )

    run_process(
        f"cmake --build {cfg.build_dir} --config {cfg.build_type}",
        setup_cmd=cfg.environment_cmd,
    )

    run_process(
        f"cmake --install {cfg.build_dir} --config {cfg.build_type}",
        setup_cmd=cfg.environment_cmd,
    )


if __name__ == "__main__":
    if sys.argv[1] == "setup":
        setup()
    elif sys.argv[1] == "build":
        build()
    else:
        print(usage)
        sys.exit(1)
