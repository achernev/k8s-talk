# {{ ansible_managed }}

concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "gitlab-runner"
  url = "https://gitlab.example.com"
  token = "{{ hostvars[groups['gitlab'][0]].gitlab_runner_authentication_token }}"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache", "/certs/client", "/usr/local/share/ca-certificates/easyrsa:/certs/easyrsa:ro", "/etc/docker/certs.d:/etc/docker/certs.d:ro"]
    shm_size = 0
    # Install the self-signed certificate inside the executor image.
    pre_build_script = """
    apk update >/dev/null
    apk add ca-certificates >/dev/null
    rm -rf /var/cache/apk/*
    cp /certs/easyrsa/ca.crt /usr/local/share/ca-certificates/ca.crt
    update-ca-certificates --fresh >/dev/null
    """
