#!/bin/bash
# Installation-time activation script for openclaw Node.js environment
# Usage: source /opt/jvs-claw/base/install-env-activate.sh
#
# WARNING: This script is for INSTALLATION ONLY!
#          Delete this file after deployment is complete.
#
# Difference from activate.sh:
#   - activate.sh: npm prefix -> user layer (for runtime)
#   - install-env-activate.sh: npm prefix -> base layer (for installation)

export OPENCLAW_ROOT="/opt/jvs-claw"
export OPENCLAW_BASE="${OPENCLAW_ROOT}/base"

# PATH: base bin only (no user layer during installation)
export PATH="${OPENCLAW_BASE}/bin:$PATH"

# NODE_PATH: base layer only
export NODE_PATH="${OPENCLAW_BASE}/lib/node_modules"

# Ensure npm installs to base layer
npm config set prefix "${OPENCLAW_BASE}"

echo "Activated openclaw INSTALLATION environment"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  npm prefix: ${OPENCLAW_BASE} (base layer)"
echo ""
echo "WARNING: 'npm install -g' will install to BASE layer!"
echo "         Delete this script after installation is complete."
