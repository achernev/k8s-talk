# syntax = docker/dockerfile:experimental
FROM python:3.9-slim AS builder

WORKDIR /usr/app

ADD . .

# You must pass in the CI_APPLICATION_TAG variable by setting the following CI/CD variable in Gitlab:
#   AUTO_DEVOPS_BUILD_IMAGE_FORWARDED_CI_VARIABLES=CI_APPLICATION_TAG
RUN --mount=type=secret,id=auto-devops-build-secrets . /run/secrets/auto-devops-build-secrets \
  set -ex && \
  pip3 install --upgrade build && \
  python3 -m build

FROM python:3.9-slim AS executor

WORKDIR /usr/app

COPY --from=builder /usr/app/dist/*.whl .
COPY scripts/wait-for-it.sh ./

RUN set -ex && \
  pip3 install --no-cache-dir *.whl && \
  chmod 0755 wait-for-it.sh && \
  groupadd -g 1000 scrooge && \
  useradd -d /usr/app -s /usr/sbin/nologin -g 1000 -M -u 1000 scrooge && \
  chown 1000:1000 .

USER scrooge

ENV SCROOGE_LOG_LEVEL="INFO"

ENTRYPOINT ["/bin/sh", "-c", "/usr/local/bin/celery -A scrooge.celeryapp worker -l ${SCROOGE_LOG_LEVEL} -B"]
