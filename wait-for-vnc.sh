#!/usr/bin/env bash
# wait-for-vnc.sh - wait for VNC server to accept connections before running the given command
set -e
HOST=${1:-127.0.0.1}
PORT=${2:-5900}
TIMEOUT=${3:-30}
shift 3 || true

echo "wait-for-vnc: waiting for ${HOST}:${PORT} (timeout ${TIMEOUT}s)"
for i in $(seq 1 $TIMEOUT); do
  if timeout 1 bash -c "cat < /dev/tcp/${HOST}/${PORT}" 2>/dev/null; then
    echo "wait-for-vnc: ${HOST}:${PORT} is reachable after ${i}s"
    exec "$@"
  fi
  sleep 1
done

echo "wait-for-vnc: timed out waiting for ${HOST}:${PORT}"
exit 1
