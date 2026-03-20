terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.2"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
  required_version = ">= 1.5"
}

provider "kind" {}

provider "helm" {
  kubernetes {
    host                   = kind_cluster.gitops.endpoint
    client_certificate     = kind_cluster.gitops.client_certificate
    client_key             = kind_cluster.gitops.client_key
    cluster_ca_certificate = kind_cluster.gitops.cluster_ca_certificate
  }
}

provider "kubernetes" {
  host                   = kind_cluster.gitops.endpoint
  client_certificate     = kind_cluster.gitops.client_certificate
  client_key             = kind_cluster.gitops.client_key
  cluster_ca_certificate = kind_cluster.gitops.cluster_ca_certificate
}

resource "kind_cluster" "gitops" {
  name = var.cluster_name
  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"
    node {
      role = "control-plane"
    }
    node {
      role = "worker"
    }
    node {
      role = "worker"
    }
  }
}

resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argocd_version
  namespace        = "argocd"
  create_namespace = true

  set {
    name  = "server.service.type"
    value = "NodePort"
  }

  set {
    name  = "server.extraArgs[0]"
    value = "--insecure"
  }

  set {
    name  = "configs.params.server\\.insecure"
    value = "true"
  }

  set {
    name  = "global.image.tag"
    value = "v2.9.3"
  }

  depends_on = [kind_cluster.gitops]
}

resource "kubernetes_namespace" "environments" {
  for_each = toset(["frontend", "backend", "monitoring"])

  metadata {
    name = each.key
    labels = {
      environment = var.environment
      managed-by  = "terraform"
    }
  }

  depends_on = [kind_cluster.gitops]
}
