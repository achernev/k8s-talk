# Gitlab with Kubernetes

## Getting EasyRSA

This directory holds the PKI used for certifying the various servers used in this project.

You must first install or download the EasyRSA package. On macOS with Homebrew you can do so with the following
commands:

```shell
brew install easyrsa
```

Other platforms may have their own packaging system equivalents, however please note that this documentation is based on
EasyRSA version 3 or better. In general, you can find the distribution for EasyRSA on [its Github releases page][1]. You
need to set the `EASYRSA_PKI` variable in your environment to point to the `easyrsa` directory before running
the `easyrsa` command to ensure that the generated PKI is placed there:

```shell
# Linux.
export EASYRSA_PKI=$(readlink -f easyrsa)

# macOS.
export EASYRSA_PKI="$(pwd -P)/easyrsa"

# Windows/PowerShell.
$env:EASYRSA_PKI = Resolve-Path easyrsa
```

## Generating Certificates

Follow the steps below to generate a certificate authority and the required certificates. Those are for UNIX-like
operating systems. Ensure that the `EASYRSA_PKI` environment variable is set up correctly.

```shell
# Initialise the PKI directory.
easyrsa init-pki

# Initialise the CA.
# You will be prompted to enter a password for the CA root certificate. Remember it.
easyrsa build-ca

# Generate a signing request for the Gitlab instance.
# Enter a memorable password when prompted.
easyrsa gen-req gitlab.example.com

# Sign the request.
# Enter the CA root certificate password when prompted.
easyrsa sign-req server gitlab.example.com

# Decrypt the private key for the issued certificate for later use in Gitlab setup.
openssl rsa -in easyrsa/private/gitlab.example.com.key -out easyrsa/private/gitlab.example.com-decrypted.key
chmod 0600 easyrsa/private/gitlab.example.com-decrypted.key

# Copy the certificates in place for the provisioning of VMs.
cp easyrsa/ca.crt vagrant-k8s/provisioning/roles/k8s/files/ca.crt
cp easyrsa/ca.crt vagrant-gitlab/provisioning/roles/common/files/ca.crt
cp easyrsa/private/gitlab.example.com-decrypted.key vagrant-gitlab/provisioning/roles/common/files/gitlab.example.com.key
cp easyrsa/issued/gitlab.example.com.crt vagrant-gitlab/provisioning/roles/common/files/gitlab.example.com.crt
```

## Note on Vagrant Providers

You must install Vagrant on the host machine for any of this to work.

The configuration implies you are using Oracle VirtualBox. If you are using a different provider you must set the
environment variable `PROVIDER`. Example follows below.

```shell
# To use the default VirtualBox provider.
vagrant up

# To use the Parallels provider on macOS.
# Before first use ensure you have installed the plugin.
vagrant plugin install vagrant-parallels
# Set the environment variable.
export PROVIDER=parallels
vagrant up
```

## Bring Up a Deployment

First, create the Kubernetes cluster by running the appropriate `vagrant up` command(s) in the `vagrant-k8s` directory.
Please see the file `README.md` in the `vagrant-k8s` directory for information on how to use the deployment.

Provided Kubernetes is up and functioning correctly, create the Gitlab and the runner VMs. To do so, run `vagrant up`
in the `vagrant-gitlab` directory.

## Creating Project in Gitlab

Once the provisioning finishes you need to do some manual work.

1. Add a line in your `/etc/hosts` (UNIX-likes) or `%WINDIR%\system32\drivers\etc\hosts` (Windows) file as follows:
   ```
   192.168.50.50 gitlab.example.com
   ```
2. Log on to Gitlab at https://gitlab.example.com/. Ignore the certificate warning and continue to the website.
   The password for user `root` can be found in `vagrant-gitlab/gitlab-root-password`.
3. Create a user for yourself in Gitlab. Mark yourself as an admin. Log on with that user.
4. Create an empty project.
5. Go to Settings -> CI/CD of that project.
6. Add the following variables in the appropriate section.

   | Name                           | Value      | Description                                                              |
   | ------------------------------ | ---------- | ------------------------------------------------------------------------ |
   | `BROWSER_PERFORMANCE_DISABLED` | `true`     | Disable browser performance testing.                                     |
   | `CODE_QUALITY_DISABLED`        | `true`     | Disable code quality metrics (these take a long time to complete).       |
   | `DOCKER_DRIVER`                | `overlay2` | Docker storage driver.                                                   |
   | `DOCKER_TLS_CERTDIR`           | `/certs`   | Docker TLS certificate directory.                                        |
   | `POSTGRES_ENABLED`             | `false`    | Disable automatic deployment of PostgreSQL (part of Gitlab Auto DevOps). |
   | `TEST_DISABLED`                | `true`     | Disable the Herokuish automatic tests (these don't support Python).      |

   For more information please refer to the [Auto DevOps customisation documentation][2].

## Additional Information

Please see the [auto deploy app notes][3] for how to structure the Helm chart. Please note that the default template
created by `helm create` differs slightly from the one expected by Gitlab. More specifically, in the values file,
the `imagePullSecrets` top-level element must be renamed to
`image.secrets`. This also needs to be reflected in the part in the templates which uses those secrets.

You must also override the name of the chart for the auto-deploy step to succeed. Create a file in your project
named `.gitlab/auto-deploy-values.yaml` which includes the line:

```yaml
# Used to work around an eccentricity of Gitlab Auto DevOps.
fullnameOverride: "production"
```

The Kubernetes setup uses the [NFS subdir external provisioner][4] for automatic provisioning of storage.

[1]: https://github.com/OpenVPN/easy-rsa/releases/
[2]: https://docs.gitlab.com/ee/topics/autodevops/customize.html
[3]: https://gitlab.com/gitlab-org/cluster-integration/auto-deploy-image/-/tree/master/assets/auto-deploy-app
[4]: https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner
