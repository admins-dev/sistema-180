#!/usr/bin/env bash
# tests/integration/helpers.sh
# Utilidades para los tests de integración SISTEMA180
set -euo pipefail

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

require_env() {
  local var="$1"
  if [ -z "${!var:-}" ]; then
    echo "ERROR: env var $var is not set."
    exit 2
  fi
}

http_get() {
  local url="$1"
  curl -s -S -H "Authorization: ${ADMIN_API_KEY}" --max-time "${CURL_TIMEOUT}" "${url}"
}

http_post() {
  local url="$1" data="$2"
  curl -s -S -X POST -H "Authorization: ${ADMIN_API_KEY}" -H "Content-Type: application/json" --max-time "${CURL_TIMEOUT}" -d "${data}" "${url}"
}

wait_for() {
  local msg="$1"; local seconds="$2"
  log "Waiting ${seconds}s for ${msg} ..."
  sleep "${seconds}"
}

assert_json_field() {
  local json_file="$1" field="$2" expected="$3"
  local actual
  actual=$(jq -r "${field}" "${json_file}" 2>/dev/null || echo "PARSE_ERROR")
  if [ "${actual}" = "${expected}" ]; then
    log "  ✅ PASS: ${field} = ${expected}"
    return 0
  else
    log "  ❌ FAIL: ${field} expected '${expected}' got '${actual}'"
    return 1
  fi
}

assert_json_not_empty() {
  local json_file="$1" field="$2"
  local actual
  actual=$(jq -r "${field}" "${json_file}" 2>/dev/null || echo "")
  if [ -n "${actual}" ] && [ "${actual}" != "null" ]; then
    log "  ✅ PASS: ${field} is not empty (=${actual})"
    return 0
  else
    log "  ❌ FAIL: ${field} is empty or null"
    return 1
  fi
}

assert_json_gt() {
  local json_file="$1" field="$2" threshold="$3"
  local actual
  actual=$(jq -r "${field}" "${json_file}" 2>/dev/null || echo "0")
  if [ "${actual}" -gt "${threshold}" ] 2>/dev/null; then
    log "  ✅ PASS: ${field} = ${actual} > ${threshold}"
    return 0
  else
    log "  ❌ FAIL: ${field} = ${actual}, expected > ${threshold}"
    return 1
  fi
}
