# Kubernetes in Vagrant

This will help you set up a Kubernetes cluster in a configurable number of VMs. There will be one designated master node
and two normal nodes by default. Change the `NODES` variable in the `Vagrantfile` to vary the latter number. Take a
moment to review the other variables at the top of that file.

You need the Kubernetes CLI tool `kubectl`.

The Kubernetes kubeconfig will be copied in this directory. You can either merge it into your `$HOME/.kube/config` (on
UNIX-like operating systems) or `%USERPROFILE%\.kube\config` (on Windows), or specify it in the environment:

```shell
# For Linux. Valid only for the current CLI session.
export KUBECONFIG="$(readlink -f kubeconfig)"

# For macOS. Valid only for the current CLI session.
export KUBECONFIG="$(pwd -P)/kubeconfig"

# For Windows/PowerShell. Valid only for the current CLI session.
$env:KUBECONFIG = Resolve-Path kubeconfig

# You can now execute kubectl.
kubectl get pods -o wide --all-namespaces
```

This setup uses the [NFS subdir external provisioner][1] for automatic provisioning of storage.

[1]: https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner
