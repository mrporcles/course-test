#!/usr/bin/env bash
# Deploys this course's LMS metadata with penguinctl.
#
#   metadata/lms/deploy.sh render      print the rendered course.json
#   metadata/lms/deploy.sh dry-run     penguinctl apply course --dry-run
#   metadata/lms/deploy.sh deploy-all  penguinctl apply course
#
# Credentials come from the environment (never commit them):
#   PENGUINCTL_APIURL, PENGUINCTL_APITOKEN
#   PENGUIN_USEDOCKER=false  use a local `penguinctl` binary instead of the Docker image
set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then set -o xtrace; fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"   # the penguinctl docker image only sees the current directory

TEMPLATE="${SCRIPT_DIR}/course.template.json"
COURSE_JSON="${SCRIPT_DIR}/course.json"
TEMPLATE_VARS='${GITHUB_REF_NAME} ${GITHUB_SHA} ${DEBUG_DATE} ${GITHUB_ACTOR} ${GITHUB_WORKFLOW}'

require-credentials() {
    : "${PENGUINCTL_APIURL:?set PENGUINCTL_APIURL (staging or production LMS API URL)}"
    : "${PENGUINCTL_APITOKEN:?set PENGUINCTL_APITOKEN}"
}

penguinctl-docker() {
    echo "penguinctl version $(docker run --rm ghcr.io/vmware-tanzu-learning/penguinctl:latest --version)"
    docker run --rm -v "$(pwd)":"$(pwd)" ghcr.io/vmware-tanzu-learning/penguinctl:latest \
        --url="${PENGUINCTL_APIURL}" --token="${PENGUINCTL_APITOKEN}" "$@"
}

penguinctl-local() {
    echo "penguinctl version $(penguinctl --version)"
    penguinctl --url="${PENGUINCTL_APIURL}" --token="${PENGUINCTL_APITOKEN}" "$@"
}

penguinctlcmd() {
    if [[ "${PENGUIN_USEDOCKER:-true}" != "false" ]]; then
        penguinctl-docker "$@"
    else
        penguinctl-local "$@"
    fi
}

render-course() {
    export GITHUB_REF_NAME="${GITHUB_REF_NAME:-$(git branch --show-current 2>/dev/null || echo local)}"
    export GITHUB_SHA="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo local)}"
    export GITHUB_ACTOR="${GITHUB_ACTOR:-${USER:-unknown}@local}"
    export GITHUB_WORKFLOW="${GITHUB_WORKFLOW:-local}"
    DEBUG_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    export DEBUG_DATE
    envsubst "${TEMPLATE_VARS}" < "${TEMPLATE}"
}

render() {
    render-course
}

apply-course() {
    require-credentials
    render-course > "${COURSE_JSON}"
    trap 'rm -f "${COURSE_JSON}"' EXIT   # course.json is generated; never keep it
    penguinctlcmd apply course "$@" -f "${COURSE_JSON}"
}

dry-run() {
    apply-course --dry-run
}

deploy-all() {
    apply-course
}

"$@"
