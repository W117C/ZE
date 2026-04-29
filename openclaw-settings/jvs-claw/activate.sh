#!/bin/bash
# Activation script for openclaw Node.js environment
# Usage: source /opt/jvs-claw/activate.sh
#
# Dual-layer structure:
#   - base/            : Fixed base packages (immutable, system-wide)
#   - ${HOME}/.npm/    : User-installed packages (per-user, npm install -g goes here)

export OPENCLAW_ROOT="/opt/jvs-claw"
export OPENCLAW_BASE="${OPENCLAW_ROOT}/base"
export OPENCLAW_USER="${HOME}/.nvm/versions/node/v24.14.0"

# Ensure user layer directory exists
mkdir -p "${OPENCLAW_USER}/lib/node_modules"
mkdir -p "${OPENCLAW_USER}/bin"

# PATH: base bin first, then user bin (base packages can override user)
export PATH="${OPENCLAW_BASE}/bin:${OPENCLAW_USER}/bin:$PATH"

# NODE_PATH: include both layers (base first for override capability)
export NODE_PATH="${OPENCLAW_BASE}/lib/node_modules:${OPENCLAW_USER}/lib/node_modules"

# Ensure npm global installs go to user layer (critical!)
"${OPENCLAW_BASE}/bin/npm" config set prefix "${OPENCLAW_USER}" 2>/dev/null
