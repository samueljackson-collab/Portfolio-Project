#!/bin/bash
set -o xtrace

# Bootstrap EKS node
/etc/eks/bootstrap.sh ${cluster_name} \
  --b64-cluster-ca '${cluster_ca}' \
  --apiserver-endpoint '${cluster_endpoint}'
