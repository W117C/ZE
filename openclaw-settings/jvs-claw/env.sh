#!/bin/bash
# Environment variables for openclaw Node.js environment
# Usage: source /opt/jvs-claw/env.sh

export OPENCLAW_ROOT=/opt/jvs-claw
export OPENCLAW_BASE=${OPENCLAW_ROOT}/base
export OPENCLAW_USER=${HOME}/.npm
mkdir -p "${OPENCLAW_USER}/lib/node_modules" "${OPENCLAW_USER}/bin" 2>/dev/null
export PATH=${OPENCLAW_USER}/bin:${OPENCLAW_BASE}/bin:$PATH
export NODE_PATH=${OPENCLAW_USER}/lib/node_modules:${OPENCLAW_BASE}/lib/node_modules
