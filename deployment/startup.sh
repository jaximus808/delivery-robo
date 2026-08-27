#!/usr/bin/env bash
# Boot script for the delivery robot Pi (user: delivery, host: raspi).
# On every start: fetch the repo, rebuild if anything changed, read
# robot_config.yaml, then launch master_launch.py in the configured mode
# (teleop / autonomous). Designed to be run by systemd (see robot.service) but works
# fine by hand: ~/delivery-robo/deployment/startup.sh
#
# Failure behavior is deliberately "start anyway": no network -> skip the pull;
# build fails -> fall back to the last good install. The robot should come up
# in the field even when GitHub is unreachable.
# No `set -u`: ROS setup.bash files reference unset vars (AMENT_TRACE_SETUP_FILES)
# and would abort the script under nounset.
set -o pipefail

REPO="${REPO:-$HOME/delivery-robo}"
WS="$REPO/ros2_ws"
BRANCH="${BRANCH:-main}"
ROS_SETUP=/opt/ros/jazzy/setup.bash
# Committed config, optionally shadowed by an untracked per-Pi override.
CONFIG="$REPO/deployment/robot_config.yaml"
[ -f "$REPO/deployment/robot_config.local.yaml" ] && CONFIG="$REPO/deployment/robot_config.local.yaml"
CONFIG="${ROBOT_CONFIG:-$CONFIG}"

log() { echo "[startup] $*"; }

cd "$REPO" || { echo "[startup] repo missing at $REPO"; exit 1; }

# --- 1. Pull if we can reach the remote (bounded so boot never hangs) -------
REBUILD=0
if timeout 20 git fetch origin "$BRANCH" 2>&1; then
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse "origin/$BRANCH")
  if [ "$LOCAL" != "$REMOTE" ]; then
    # ff-only: refuses instead of clobbering local edits made on the Pi.
    if git merge --ff-only "origin/$BRANCH"; then
      log "updated $LOCAL -> $(git rev-parse --short HEAD), will rebuild"
      REBUILD=1
    else
      log "WARNING: local changes on the Pi diverge from origin/$BRANCH."
      log "WARNING: running the OLD code. Commit/stash on the Pi to resume updates."
    fi
  else
    log "already up to date at $(git rev-parse --short HEAD)"
  fi
else
  log "fetch failed (offline?) — starting with the existing build"
fi

# --- 2. Build if updated or never built ------------------------------------
[ -f "$WS/install/setup.bash" ] || REBUILD=1
if [ "$REBUILD" = 1 ]; then
  log "building ros2_ws..."
  # shellcheck disable=SC1090
  source "$ROS_SETUP"
  if (cd "$WS" && colcon build --symlink-install); then
    log "build ok"
  else
    log "WARNING: build FAILED — falling back to the previous install"
  fi
fi

# --- 3. Read the robot config ----------------------------------------------
# Top-level "key: value" only; no yq/python dependency so boot can't fail on it.
cfg_get() { sed -n "s/^[[:space:]]*$1:[[:space:]]*\([^#]*\).*/\1/p" "$CONFIG" | head -n1 | xargs; }
MODE=""
if [ -f "$CONFIG" ]; then
  MODE=$(cfg_get mode)
  log "config $CONFIG"
else
  log "WARNING: config $CONFIG not found"
fi
MODE="${MODE:-teleop}"
case "$MODE" in
  teleop|autonomous) ;;
  *) log "WARNING: unknown mode '$MODE', falling back to teleop"; MODE=teleop ;;
esac

# --- 4. Launch -------------------------------------------------------------
# shellcheck disable=SC1090
source "$ROS_SETUP"
# shellcheck disable=SC1090
source "$WS/install/setup.bash"
log "launching my_bringup master_launch.py mode:=$MODE"
exec ros2 launch my_bringup master_launch.py "mode:=$MODE"
