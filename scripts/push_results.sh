#!/usr/bin/env bash
# Push RQ1/RQ2 result files back to the repo so a `git pull` on your laptop pulls
# them in. Run from the repo root on the GPU box, with a GitHub token that has
# write (contents) access to cliprompter/creditaudit:
#
#   GITHUB_TOKEN=ghp_xxx bash scripts/push_results.sh
#
# The token is used only in the push URL (not stored in .git/config). It still
# lands in your shell history — use a short-lived / fine-grained token.
set -euo pipefail

: "${GITHUB_TOKEN:?set GITHUB_TOKEN (GitHub PAT with write access) first}"
REMOTE="https://${GITHUB_TOKEN}@github.com/cliprompter/creditaudit.git"

git config user.name  "${GIT_NAME:-results-bot}"
git config user.email "${GIT_EMAIL:-results-bot@users.noreply.github.com}"

git add experiments/rq1 experiments/rq2
if git diff --cached --quiet; then
  echo "Tidak ada hasil baru untuk di-commit (jalankan eksperimen dulu)."
  exit 0
fi

git commit -m "Add RQ1/RQ2 results (auto-push from GPU run)"
git push "$REMOTE" HEAD:master
echo "OK: hasil ter-push ke master. Di laptop jalankan: git pull"
