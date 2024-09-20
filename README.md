# PrusaSlicer autobuild

This repository aims to provide the tools necessary to build PrusaSlicer cross platform. It is mainly meant to be used as part of a CI workflow but can also be used during local development.

## Build as part of github workflow

### Using per platform build workflows
This repository provides the following reusable workflows:
+ `.github/workflows/build_linux.yml`
+ `.github/workflows/build_windows.yml`
+ `.github/workflows/build_macos.yml`

They may be used for per platform builds of PrusaSlicer. The generated binaries of PrusaSlicer are uploaded as build artifacts to the workflow.

#### Workflow inputs
The platform specific build workflows all require the following inputs:

+  <b>upstream_repo</b><br>
The upstream repository of PrusaSlicer. Usually set to `prusa3d/PrusaSlicer`.

+ <b>upstream_ref:</b><br>
The actual branch or tag the build will be rebased on. Use `<branch>` for branches, `tag:<tag>` for tags.

+ <b>downstream_repo:</b><br>
The repository (usually a fork) containing the feature branches for PrusaSlicer.

+ <b>downstream_feature_branches:</b><br>
A semicolon separated list of feature branch names. They will be rebased on top of one-another, starting with `upstream_ref` as a base.

### Using integrated autobuild workflow
The `.github/workflows/autobuild.yml` workflow can be used for parallel builds on all three platforms. This workflow also provides additional functionality for automatically creating a release of PrusaSlicer with the additional features, when a new release is added to the `upstream_repo`.

#### Workflow inputs
The workflow requires same inputs as specified above. Additionally these inputs may be specified:

+ <b>only_if_new_release:</b><br>
Boolean, if set to true, a build will only be executed if the newest release (tag) on `upstream_repo` is not present on `downstream_repo`.

+ <b>create_release_copy:</b><br>
<i>Requires `only_if_new_release` to be set.</i><br>
Boolean specifying if a copy release should be created for `downstream_repo` containing the built binaries. The copy release will include the same name and body as the respective release on `upstream_repo`.

+ <b>release_tag_prefix:</b><br>
<i>Optional, Requires `create_release_copy` to be set.</i><br>
The prefix added to the release tag on `downstream_repo` to avoid naming collisions with existing tags. The default prefix is `autobuild_`.

+ <b>release_name_prefix:</b><br>
<i>Optional, Requires `create_release_copy` to be set.</i><br>
Prefix for the `downstream_repo` release title. By default not prefix is added.

+ <b>release_body_prefix:</b><br>
<i>Optional, Requires `create_release_copy` to be set.</i><br>
Prefix for the `downstream_repo` release body. By default not prefix is added.

When using the `only_if_new_release` and `create_release_copy` functionality, the `upstream_ref` input should be set to `latest:release`. This ensures that the created copy release is actually based on the repository state of the copied release.

#### Automatic release generation
For automatic release generation the workflow is best invoked periodically on a schedule. Please also make sure the workflow has write access to the repository.

An example trigger workflow (present on the `downstream_repo`) may look like this:

```yaml
# File @ .github/workflows/example_trigger.yml

name: PrusaSlicer autobuild example trigger

on:
  workflow_dispatch:
  schedule:
    - cron: '0 */12 * * *'

jobs:
  trigger-autobuild:
    uses: Felix-Rm/prusaslicer-autobuild/.github/workflows/autobuild.yml@main
    with:
      only_if_new_release: true
      create_release_copy: true
      upstream_repo: prusa3d/PrusaSlicer
      upstream_ref: latest:release
      downstream_repo: Felix-Rm/prusaslicer-autobuild # replace with your fork
      downstream_feature_branches: ';' # replace with your feature branches, seperated by ';'
      release_tag_prefix: 'autobuild_'
      release_name_prefix: 'Autobuild for Release of '
      release_body_prefix: |
        This is an autobuild release of PrusaSlicer.
        There are no guarantees that this build is stable, no additional testing has been done.
    secrets:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Build locally

This repository also includes the resources for setting up a build environment and building locally on your machine.

### Building directly on host OS

#### Setting up build and PrusaSlicer dependencies

Shell scripts for setting up the build environment are located in the `build_environment` directory. <b>Please note that they will install additional software and modify configurations on your system. Reading through the scripts and potentially executing (only the necessary) commands by hand is strongly recommended.</b>

#### Cloning and rebasing the PrusaSlicer source

To achieve the same functionality as the CI workflows the following command may be executed: `python3 runner.py setup <config.yml>`.

This will check out and setup the PrusaSlicer source tree as specified in the configuration file. The configuration file needs to include the following keys:
+ <b>upstream_repo:</b> See "Build as part of github workflow" section.
+ <b>upstream_ref:</b> See "Build as part of github workflow" section.
+ <b>downstream_repo:</b> See "Build as part of github workflow" section.
+ <b>downstream_feature_branches:</b> See "Build as part of github workflow" section.
+ <b>checkout_dir:</b> The directory the sources will be placed in.

See the `example_config_*.yml` files for configuration examples.

<b>It is not recommended to use this command when building directly on the host as it will modify the global git configuration on your system. See the "Isolated building with Docker" below. Skipping this command may result in some build commands (mainly the install step on windows) not working completely as no source patches will be applied. Applying the patches in the `patches` repository by hand is recommended in this case.</b>

#### Building PrusaSlicer

To start the actual build, the following command may be used: `python3 runner.py build <config.yml>`.

This will build and install PrusaSlicer in the directories specified in the configuration file.

The configuration file needs to include the following keys:
+ <b>checkout_dir:</b> The directory the sources will be placed in.
+ <b>build_dir:</b> The directory the main build will be placed in.
+ <b>build_dep_dir:</b> The directory the build of dependencies will be placed in.
+ <b>install_dir:</b> The directory PrusaSlicer will be installed in
+ <b>build_type:</b> The build type / configuration.
+ <b>cmake_flags:</b> Any additional cmake flags.
+ <b>environment_cmd:</b> Command for setting up build environment.

See the `example_config_*.yml` files for configuration examples.

### Isolated building with Docker

<i>Please note that running Windows containers in Docker is currently not possible on Windows Home edition. Windows Professional, Enterprise or Server is required.</i>

For builds on Linux and Windows this repository provides docker compose files. This has the benefit of not needing to install any dependencies of PrusaSlicer on your local machine.

Before actually running docker compose, the `SETUP_CONFIG` environment variable should be set to point to your configuration file as described in the previous steps. If this variable is not set, the compose file defaults to `config.yml`. Please note that all paths described in the configuration file must reside inside the repository root, as they will be mounted into the docker container while building.

Additionally the `DOCKER_USER` environment variable may be set to `root` or `ContainerAdministrator` on Linux and Windows respectively to build using root / admin privileges. Please note that this might lead to permission problems with generated files.

When running the compose file the root of this repository will be mounted into the docker container. This makes any generated files persistent by storing them on the host filesystem.

If the `checkout_dir` directory is not yet present or needs updating, run the following command first: `docker compose -f compose_<os>.yml up autosetup --build`. This will run the equivalent of `python3 runner.py setup <config.yaml>` inside the docker container. The step may be skipped if the local development sources are located at `checkout_dir`.

After the `checkout_dir` is setup as required, the actual build can be started with `docker compose -f compose_<os>.yml up autobuild --build`.

