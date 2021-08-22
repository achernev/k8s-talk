# My Awesome Project

Just an example project to demonstrate Gitlab Auto DevOps' default settings.

To have Gitlab successfully build this you need to do some manual work. The steps below assume you are using the bundled
Gitlab/Kubernetes deployment.

1. Add a line in your `/etc/hosts` (UNIX-likes) or `%WINDIR%\system32\drivers\etc\hosts` (Windows) file as follows:
   ```
   192.168.50.10 my-awesome-project.example.com
   ```
2. Log on to Gitlab.
3. Create an empty project called `my-awesome-project` (the name needs to match the hosts file entry above).
4. Go to Settings -> CI/CD of that project.
5. Add the following variables in the appropriate section.

   | Name                           | Value      | Description                                                              |
   | ------------------------------ | ---------- | ------------------------------------------------------------------------ |
   | `BROWSER_PERFORMANCE_DISABLED` | `true`     | Disable browser performance testing.                                     |
   | `CODE_QUALITY_DISABLED`        | `true`     | Disable code quality metrics (these take a long time to complete).       |
   | `DOCKER_DRIVER`                | `overlay2` | Docker storage driver.                                                   |
   | `DOCKER_TLS_CERTDIR`           | `/certs`   | Docker TLS certificate directory.                                        |
   | `POSTGRES_ENABLED`             | `false`    | Disable automatic deployment of PostgreSQL (part of Gitlab Auto DevOps). |
   | `TEST_DISABLED`                | `true`     | Disable the Herokuish automatic tests (these don't support Python).      |

   For more information please refer to the [Auto DevOps customisation documentation][1].
6. Push the code to the repository and then monitor the CI/CD section in Gitlab for build status.

## Additional Information

Please see the [auto deploy app notes][2] for how to structure the Helm chart. Please note that the default template
created by `helm create` differs slightly from the one expected by Gitlab. More specifically, in the values file,
the `imagePullSecrets` top-level element must be renamed to
`image.secrets`. This also needs to be reflected in the part in the templates which uses those secrets.

You must also override the name of the chart for the auto-deploy step to succeed. Create a file in your project
named `.gitlab/auto-deploy-values.yaml` which includes the line:

```yaml
# Used to work around an eccentricity of Gitlab Auto DevOps.
fullnameOverride: "production"
```

[1]: https://docs.gitlab.com/ee/topics/autodevops/customize.html

[2]: https://gitlab.com/gitlab-org/cluster-integration/auto-deploy-image/-/tree/master/assets/auto-deploy-app
