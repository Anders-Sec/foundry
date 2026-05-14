#!/usr/bin/env bash
# Verifies that the commit message contains a DCO Signed-off-by line.
# Called as a commit-msg hook by pre-commit.
set -euo pipefail

commit_msg_file="${1}"

if ! grep -qE "^Signed-off-by: .+ <.+@.+>$" "${commit_msg_file}"; then
  echo ""
  echo "ERROR: Commit is missing a DCO Signed-off-by line."
  echo ""
  echo "  Add it with:  git commit -s"
  echo "  Or manually:  Signed-off-by: Full Name <email@example.com>"
  echo ""
  echo "See https://developercertificate.org for details."
  exit 1
fi
