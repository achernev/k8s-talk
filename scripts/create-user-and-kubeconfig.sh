#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

usage() {
  echo "Usage: $0 -u <username> -n <namespace> [-c <cluster name>]" 1>&2
  exit 1
}

cleanup() {
  echo 'Cleaning up.'
  if [ -n "${USERNAME-}" ]; then
    rm -f "${USERNAME}-csr.yaml"
    rm -f "${USERNAME}.key"
    rm -f "${USERNAME}.csr"
    rm -f "${USERNAME}.crt"
  fi
  if [ -n "${NAMESPACE-}" ]; then
    rm -f "${NAMESPACE}-admin.yaml"
  fi
  if [ -n "${CLUSTER-}" ]; then
    rm -f "${CLUSTER}-ca.crt"
  else
    rm -f kubernetes-ca.crt
  fi
}

trap cleanup INT TERM EXIT

while getopts ":u:n:c:" o; do
  case "${o}" in
  u)
    USERNAME=${OPTARG}
    ;;
  n)
    NAMESPACE=${OPTARG}
    ;;
  c)
    CLUSTER=${OPTARG}
    ;;
  *)
    usage
    ;;
  esac
done

shift $((OPTIND - 1))

if [ -z "${USERNAME-}" ] || [ -z "${NAMESPACE-}" ]; then
  usage
fi

if [ -z "${CLUSTER-}" ]; then
  CLUSTER='kubernetes'
fi

echo "Username: ${USERNAME}"
echo "Namespace: ${NAMESPACE}"
echo "Cluster: ${CLUSTER}"

echo 'Generating user key.'
openssl genrsa -out "${USERNAME}.key" 2048 &>/dev/null
echo 'Generating certificate signing request.'
openssl req -new -key "${USERNAME}.key" -out "${USERNAME}.csr" -subj "/CN=${USERNAME}"

cat <<EOF >"${USERNAME}-csr.yaml"
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: ${USERNAME}
spec:
  request: $(base64 <"${USERNAME}.csr" | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
EOF

echo 'Creating certificate signing request in Kubernetes.'
kubectl create -f "${USERNAME}-csr.yaml"

echo 'Approving certificate signing request in Kubernetes.'
kubectl certificate approve "${USERNAME}"

echo 'Fetching user certificate from Kubernetes.'
kubectl get csr "${USERNAME}" -o jsonpath='{.status.certificate}' | base64 --decode >"${USERNAME}.crt"

cat <<EOF >"${NAMESPACE}-admin.yaml"
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ${NAMESPACE}-admin
  namespace: ${NAMESPACE}
rules:
- apiGroups:
  - ""
  resources:
  - pods/attach
  - pods/exec
  - pods/portforward
  - pods/proxy
  - secrets
  - services/proxy
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - serviceaccounts
  verbs:
  - impersonate
- apiGroups:
  - ""
  resources:
  - pods
  - pods/attach
  - pods/exec
  - pods/portforward
  - pods/proxy
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - ""
  resources:
  - configmaps
  - endpoints
  - persistentvolumeclaims
  - replicationcontrollers
  - replicationcontrollers/scale
  - secrets
  - serviceaccounts
  - services
  - services/proxy
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - apps
  resources:
  - daemonsets
  - deployments
  - deployments/rollback
  - deployments/scale
  - replicasets
  - replicasets/scale
  - statefulsets
  - statefulsets/scale
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - autoscaling
  resources:
  - horizontalpodautoscalers
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - batch
  resources:
  - cronjobs
  - jobs
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - extensions
  resources:
  - daemonsets
  - deployments
  - deployments/rollback
  - deployments/scale
  - ingresses
  - networkpolicies
  - replicasets
  - replicasets/scale
  - replicationcontrollers/scale
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - policy
  resources:
  - poddisruptionbudgets
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - networking.k8s.io
  resources:
  - ingresses
  - networkpolicies
  verbs:
  - create
  - delete
  - deletecollection
  - patch
  - update
- apiGroups:
  - ""
  resources:
  - configmaps
  - endpoints
  - persistentvolumeclaims
  - persistentvolumeclaims/status
  - pods
  - replicationcontrollers
  - replicationcontrollers/scale
  - serviceaccounts
  - services
  - services/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - bindings
  - events
  - limitranges
  - namespaces/status
  - pods/log
  - pods/status
  - replicationcontrollers/status
  - resourcequotas
  - resourcequotas/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - namespaces
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - apps
  resources:
  - controllerrevisions
  - daemonsets
  - daemonsets/status
  - deployments
  - deployments/scale
  - deployments/status
  - replicasets
  - replicasets/scale
  - replicasets/status
  - statefulsets
  - statefulsets/scale
  - statefulsets/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - autoscaling
  resources:
  - horizontalpodautoscalers
  - horizontalpodautoscalers/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - batch
  resources:
  - cronjobs
  - cronjobs/status
  - jobs
  - jobs/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - extensions
  resources:
  - daemonsets
  - daemonsets/status
  - deployments
  - deployments/scale
  - deployments/status
  - ingresses
  - ingresses/status
  - networkpolicies
  - replicasets
  - replicasets/scale
  - replicasets/status
  - replicationcontrollers/scale
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - policy
  resources:
  - poddisruptionbudgets
  - poddisruptionbudgets/status
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - networking.k8s.io
  resources:
  - ingresses
  - ingresses/status
  - networkpolicies
  verbs:
  - get
  - list
  - watch
EOF

kubectl apply -f "${NAMESPACE}-admin.yaml"

# User is limited only to the namespace (cannot control PVs and other cluster-level resources).
#kubectl create role developer --verb=create --verb=get --verb=list --verb=update --verb=delete --resource=pods --namespace="${NAMESPACE}"
kubectl create rolebinding "${USERNAME}-${NAMESPACE}-admin" \
  --role="${NAMESPACE}-admin" \
  --user="${USERNAME}" \
  --namespace="$NAMESPACE"

# User is on the cluster level.
#kubectl create clusterrolebinding "${USERNAME}-cluster-admin" \
#  --clusterrole=cluster-admin \
#  --user="${USERNAME}" \
#  --group=system:serviceaccounts

API_SERVER="$(kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " ")"

kubectl config view --raw --minify | \
  grep certificate-authority-data | \
  awk -F: '{ print $2 }' | \
  tr -d " " | \
  base64 --decode >"${CLUSTER}-ca.crt"

kubectl config set-cluster "${CLUSTER}" \
  --certificate-authority="${CLUSTER}-ca.crt" \
  --embed-certs=true \
  --server="${API_SERVER}" \
  --kubeconfig="${USERNAME}.kubeconfig"

kubectl config set-credentials "${USERNAME}" \
  --client-certificate="${USERNAME}.crt" \
  --client-key="${USERNAME}.key" \
  --embed-certs=true \
  --kubeconfig="${USERNAME}.kubeconfig"

kubectl config set-context "${CLUSTER}" \
  --cluster="${CLUSTER}" \
  --user="${USERNAME}" \
  --namespace="$NAMESPACE" \
  --kubeconfig="${USERNAME}.kubeconfig"

kubectl config use-context "${CLUSTER}" --kubeconfig="${USERNAME}.kubeconfig"

echo "Finished. Kubeconfig: ${USERNAME}.kubeconfig"
