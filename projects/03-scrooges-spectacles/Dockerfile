# syntax = docker/dockerfile:experimental
FROM python:3.9-slim AS executor

WORKDIR /usr/app

# Add the requirements file alone before fulfilling it to avoid
# full rebuilds if the other code changes.
ADD requirements.txt .

# You must pass in the CI_REGISTRY_USER and CI_JOB_TOKEN variables by setting the following CI/CD variable in Gitlab:
#   AUTO_DEVOPS_BUILD_IMAGE_FORWARDED_CI_VARIABLES=CI_REGISTRY_USER,CI_JOB_TOKEN
# This is done in the .gitlab-ci.yml file.
RUN --mount=type=secret,id=auto-devops-build-secrets . /run/secrets/auto-devops-build-secrets \
  set -ex && \
  pip3 install --no-cache-dir -r requirements.txt

ADD spectacles spectacles

RUN set -ex && \
  groupadd -g 1000 scrooge && \
  useradd -d /usr/app -s /usr/sbin/nologin -g 1000 -M -u 1000 scrooge && \
  chown 1000:1000 .

USER scrooge

ENTRYPOINT ["python3", "-m", "spectacles"]
