# {{ ansible_managed }}
external_url 'https://gitlab.example.com'
registry_external_url 'https://gitlab.example.com:5050'
nginx['redirect_http_to_https'] = true
letsencrypt['enable'] = false
