#!/bin/sh
# prepare-jktz-venv.sh — Docker ENTRYPOINT for the jktz-survex image.
#
# The container expects the host repo bind-mounted at /project. This script:
#   1. cd /project so uv finds pyproject.toml + uv.lock from the bind mount.
#   2. uv sync --locked — installs the jktz package editable into
#      /opt/jktz-venv (set by UV_PROJECT_ENVIRONMENT). Runtime deps were
#      pre-fetched at image build, so this only links src/jktz, fast.
#   3. exec "$@" — replaces this shell with whatever command was passed to
#      `docker run`, typically `uv run jktz-validate` / `jktz-exports` / ...
set -e

cd /project
uv sync --locked

exec "$@"
