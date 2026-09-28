#!/bin/bash
# Local-only WeAct routing; tools are supplied via environment, not downloaded.
set -eu
cd "$(dirname "$0")/.."
: "${ROUTER_JAVA:?Set ROUTER_JAVA to Java 25 executable}"
: "${ROUTER_JAR:?Set ROUTER_JAR to Freerouting 2.4.1 jar}"
"$ROUTER_JAVA" -Djava.awt.headless=true -jar "$ROUTER_JAR" \
 --user_data_path=tmp/weact-routing/userdata --gui.enabled=false \
 --api_server.enabled=false --mcp_server.enabled=false \
 --profile.allow_telemetry=false --profile.allow_contact=false -da -dl \
 -de tmp/weact-routing/route.dsn -do tmp/weact-routing/route.ses \
 -dr tmp/weact-routing/route.rules -inc GROUND -mp 40 -mt 1 -l en \
 > tmp/weact-routing/router.log 2>&1
