# Azure Compute Module
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type    = string
  default = "East US"
}

variable "vm_size" {
  type    = string
  default = "Standard_B1s"
}

variable "subnet_id" {
  type = string
}

resource "azurerm_public_ip" "app" {
  name                = "${var.environment}-app-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_network_interface" "app" {
  name                = "${var.environment}-app-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.app.id
  }

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_linux_virtual_machine" "app" {
  name                = "${var.environment}-app-vm"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = var.vm_size
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.app.id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  custom_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y nginx
              systemctl start nginx
              systemctl enable nginx
              EOF
  )

  tags = {
    Environment = var.environment
  }
}

output "vm_id" {
  value = azurerm_linux_virtual_machine.app.id
}

output "public_ip" {
  value = azurerm_public_ip.app.ip_address
}

output "private_ip" {
  value = azurerm_network_interface.app.private_ip_address
}
