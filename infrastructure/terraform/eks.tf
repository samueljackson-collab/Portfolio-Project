data "aws_eks_cluster" "portfolio" {
  name = aws_eks_cluster.portfolio.id
}

data "aws_eks_cluster_auth" "portfolio" {
  name = aws_eks_cluster.portfolio.id
}

resource "aws_iam_role" "eks_cluster" {
  name               = "${local.name_prefix}-eks-cluster"
  assume_role_policy = data.aws_iam_policy_document.eks_trust.json

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-eks-cluster-role"
  })
}

data "aws_iam_policy_document" "eks_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_eks_cluster" "portfolio" {
  name     = "${local.name_prefix}"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.eks_version

  vpc_config {
    subnet_ids              = concat(values(aws_subnet.public)[*].id, values(aws_subnet.private)[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.api_public_cidrs
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = merge(local.common_tags, {
    "Name" = local.name_prefix
  })
}

resource "aws_iam_role" "eks_node_group" {
  name               = "${local.name_prefix}-eks-node"
  assume_role_policy = data.aws_iam_policy_document.eks_node_trust.json

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-eks-node-role"
  })
}

data "aws_iam_policy_document" "eks_node_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "eks_worker_node" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  ])

  role       = aws_iam_role.eks_node_group.name
  policy_arn = each.key
}

resource "aws_eks_node_group" "portfolio" {
  cluster_name    = aws_eks_cluster.portfolio.name
  node_group_name = "${local.name_prefix}-app"
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = values(aws_subnet.private)[*].id

  scaling_config {
    desired_size = var.eks_desired_nodes
    max_size     = var.eks_max_nodes
    min_size     = var.eks_min_nodes
  }

  update_config {
    max_unavailable = 1
  }

  instance_types = [var.eks_instance_type]
  disk_size      = 50

  labels = {
    "workload" = "portfolio-api"
  }

  tags = merge(local.common_tags, {
    "Name" = "${local.name_prefix}-node-group"
  })
}
