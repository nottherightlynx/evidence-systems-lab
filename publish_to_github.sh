#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SITE="https://evidencesystemslapbylmchea.lovable.app/"
if ! command -v git >/dev/null 2>&1; then echo "Git is required: https://git-scm.com/downloads"; exit 1; fi
if ! command -v gh >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    echo "Installing GitHub CLI with Homebrew ..."
    brew install gh
  else
    echo "Install GitHub CLI from https://cli.github.com/ and rerun this script."; exit 1
  fi
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "Authenticate to GitHub using the browser ..."
  gh auth login --web --git-protocol https
fi
LOGIN="$(gh api user --jq .login)"
if [[ -z "$LOGIN" ]]; then echo "Cannot determine logged-in GitHub account"; exit 1; fi
BASE='evidence-systems-lab'
REPO="$BASE"
N=2
while gh repo view "$LOGIN/$REPO" >/dev/null 2>&1; do
  REPO="${BASE}-${N}"
  N=$((N+1))
done
if [[ ! -d .git ]]; then git init -b main; fi
if ! git config user.name >/dev/null; then git config user.name "$LOGIN"; fi
if ! git config user.email >/dev/null; then
  ID="$(gh api user --jq .id)"
  git config user.email "${ID}+${LOGIN}@users.noreply.github.com"
fi
git add .
if ! git diff --cached --quiet; then git commit -m "Publish reproducible evidence systems lab"; fi
echo "Creating public repository $LOGIN/$REPO ..."
gh repo create "$LOGIN/$REPO" --public --description "Evidence-first analytics engineering: dbt CRM modeling, Dagster public-data observability, and governed metrics" --source=. --remote=origin --push
URL="$(gh repo view "$LOGIN/$REPO" --json url --jq .url)"
cat > EMAIL_TO_SEND.txt <<EOF
Subject: Evidence Systems Lab | Three connections ahead of Wednesday

Hi,

While preparing for our Wednesday conversation, I built a synthetic-data Evidence Systems Lab because I saw three parallels between the role and my work on the CFLeads CRM transition and NCTE public-data systems.
First, the dbt models explore preserving identity and business definitions during CRM changes; second, the Dagster pipeline makes source freshness and cross-jurisdiction failures observable; and third, the governed query interface returns traceable metrics while refusing unsupported requests.
I put the project walkthrough at $SITE and the reproducible code at $URL.
How is your team balancing a clear throughline across data sources with identity mapping between CRMs and continuity of essential reporting during the transition?

Best,
Lynx
EOF
printf '\nPUBLISHED REPOSITORY: %s\nPORTFOLIO SITE: %s\n\n' "$URL" "$SITE"
echo 'Your final email, with BOTH verified links, is saved to EMAIL_TO_SEND.txt.'
if command -v pbcopy >/dev/null 2>&1; then pbcopy < EMAIL_TO_SEND.txt; echo 'Your completed email has also been copied to the clipboard.'; fi
