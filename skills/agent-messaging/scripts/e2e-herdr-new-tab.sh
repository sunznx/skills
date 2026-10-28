#!/usr/bin/env bash
# End-to-end check of the "new Herdr tab" flow in agent-messaging, against the real Herdr server.
# For each agent kind: create a tab in the test workspace, start the agent, prompt a small task,
# wait for `working`, read the reply, then close the tab and confirm nothing is left.
#
# Usage: e2e-herdr-new-tab.sh [KIND ...]          (default: claude)
# Env:   E2E_WORKSPACE_LABEL  test workspace label (default: scratch; created and closed if missing)
#        E2E_CWD              cwd for the new tab (default: $PWD; the agent must already trust it)
#        E2E_START_TIMEOUT_MS agent start timeout (default: 90000)
#        E2E_REPLY_TIMEOUT_MS wait for the reply (default: 180000)
set -euo pipefail

if [ "${HERDR_ENV:-}" != "1" ]; then
  echo "SKIP: HERDR_ENV is not 1. This shell is not in a Herdr pane, so it cannot drive Herdr."
  exit 0
fi
for tool in herdr jq; do
  command -v "$tool" >/dev/null || { echo "FAIL: $tool is not on PATH"; exit 1; }
done

label=${E2E_WORKSPACE_LABEL:-scratch}
cwd=${E2E_CWD:-$PWD}
start_ms=${E2E_START_TIMEOUT_MS:-90000}
reply_ms=${E2E_REPLY_TIMEOUT_MS:-180000}
[ "$#" -gt 0 ] || set -- claude

open_tabs=""
created_ws=""
failures=0

close_tab() {
  herdr tab close "$1" >/dev/null 2>&1 || true
  open_tabs=$(printf '%s\n' $open_tabs | grep -vx "$1" || true)
}
cleanup() {
  for tab in $open_tabs; do close_tab "$tab"; done
  if [ -n "$created_ws" ]; then
    herdr workspace close "$created_ws" >/dev/null 2>&1 || echo "WARN: could not close workspace $created_ws"
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

fail() { echo "FAIL [$1] $2"; failures=$((failures + 1)); }

ws=$(herdr workspace list | jq -r --arg l "$label" '[.result.workspaces[] | select(.label == $l)][0].workspace_id // empty')
if [ -z "$ws" ]; then
  ws=$(herdr workspace create --cwd "$cwd" --label "$label" --no-focus | jq -r '.result.workspace.workspace_id')
  created_ws=$ws
  echo "info: created workspace $ws ($label)"
fi
echo "info: workspace $ws ($label), cwd $cwd"

run_kind() {
  local kind=$1 name tab pane out status a b expected
  name="e2e-${kind}-$(date +%s)$((RANDOM % 100))"
  name=${name:0:32}

  out=$(herdr tab create --workspace "$ws" --cwd "$cwd" --label "$name" --env "E2E_RUN=$name" --no-focus) \
    || { fail "$kind" "tab create: $out"; return; }
  tab=$(jq -r '.result.tab.tab_id' <<<"$out")
  pane=$(jq -r '.result.root_pane.pane_id' <<<"$out")
  open_tabs="$open_tabs $tab"
  echo "ok   [$kind] tab $tab, pane $pane"

  if ! out=$(herdr agent start "$name" --kind "$kind" --pane "$pane" --timeout "$start_ms" 2>&1); then
    fail "$kind" "agent start: $out"
    close_tab "$tab"
    return
  fi
  if ! jq -e '.result.type == "agent_started" and .result.agent.interactive_ready == true' <<<"$out" >/dev/null 2>&1; then
    fail "$kind" "agent start did not report agent_started with interactive_ready: $out"
    close_tab "$tab"
    return
  fi
  echo "ok   [$kind] agent_started, interactive_ready"

  a=$((RANDOM % 50 + 10)); b=$((RANDOM % 50 + 10)); expected="ack-$((a + b))"
  herdr agent prompt "$name" "agent-messaging e2e test. Compute $a + $b and reply with only ack- followed by the result, as in ack-0. Run no commands, edit no files, and notify no one." >/dev/null \
    || { fail "$kind" "agent prompt"; close_tab "$tab"; return; }

  if herdr agent wait "$name" --until working --timeout 60000 >/dev/null 2>&1; then
    echo "ok   [$kind] status became working"
  else
    fail "$kind" "status never became working: $(herdr agent get "$name" 2>&1 | jq -r '.result.agent.agent_status // .' 2>/dev/null)"
  fi

  herdr agent wait "$name" --until idle --until done --timeout "$reply_ms" >/dev/null 2>&1 \
    || fail "$kind" "no settled state within ${reply_ms}ms"
  if herdr agent read "$name" --source recent-unwrapped --lines 60 | grep -q -- "$expected"; then
    echo "ok   [$kind] reply contains $expected"
  else
    fail "$kind" "reply has no $expected"
  fi

  close_tab "$tab"
  if herdr tab get "$tab" >/dev/null 2>&1; then fail "$kind" "tab $tab still open"; fi
  if herdr agent get "$name" >/dev/null 2>&1; then fail "$kind" "agent $name still live"; fi
  echo "ok   [$kind] closed $tab, nothing left"
}

for kind in "$@"; do run_kind "$kind"; done

if [ "$failures" -eq 0 ]; then echo "PASS: $*"; else echo "FAIL: $failures check(s) failed"; exit 1; fi
