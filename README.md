# Gitlab with Kubernetes

## Getting EasyRSA

The `easyrsa` directory is there to house a PKI used for certifying the various servers used in this project.

You must first install or download the EasyRSA package. On macOS with Homebrew you can do so with the following
commands:

```shell
brew install easy-rsa
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

# Generate a signing request for the Harbor instance.
# Enter a memorable password when prompted.
easyrsa gen-req registry.example.com

# Sign the request.
# Enter the CA root certificate password when prompted.
easyrsa sign-req server registry.example.com

# Decrypt the private keys for the issued certificates for later use in Gitlab and Harbor setup.
openssl rsa -in easyrsa/private/gitlab.example.com.key -out easyrsa/private/gitlab.example.com-decrypted.key
openssl rsa -in easyrsa/private/registry.example.com.key -out easyrsa/private/registry.example.com-decrypted.key
chmod 0600 easyrsa/private/gitlab.example.com-decrypted.key
chmod 0600 easyrsa/private/registry.example.com-decrypted.key

# Copy the certificates in place for the provisioning of VMs.
cp easyrsa/ca.crt vagrant-k8s/provisioning/roles/k8s/files/ca.crt
cp easyrsa/ca.crt vagrant-gitlab/provisioning/roles/common/files/ca.crt
cp easyrsa/private/gitlab.example.com-decrypted.key vagrant-gitlab/provisioning/roles/common/files/gitlab.example.com.key
cp easyrsa/issued/gitlab.example.com.crt vagrant-gitlab/provisioning/roles/common/files/gitlab.example.com.crt
# Harbor
cp easyrsa/private/registry.example.com-decrypted.key harbor/config/ssl/certs/registry.example.com.key
cp easyrsa/issued/registry.example.com.crt harbor/config/ssl/certs/registry.example.com.crt
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

[1]: https://github.com/OpenVPN/easy-rsa/releases/
