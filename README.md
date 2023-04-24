# Scripting with pyGNMI to troubleshoot Datacenters

Welcome to this tutorial where we will guide you through the creation of a network lab using containerlab. Specifically, we will be focusing on the Spine/Leaf + Border-Leaf Datacenter Architecture, using technologies such as Layer 2/3 EVPN-VXLAN and eBGP for Underlay.

We will cover everything you need to know about creating a virtual network environment that emulates a real-world network, complete with routing protocols and traffic flow. You will learn how to install the necessary requirements for pyGNMI scripting, a powerful tool that allows you to operate and troubleshoot EVPN-VXLAN design.

By the end of this tutorial, you will be able to script in pyGNMI to perform various tasks in your virtual network environment. This will give you a deeper understanding of how networks operate and enable you to troubleshoot and optimize network performance. Whether you are an experienced network engineer or just starting, this tutorial will provide valuable insights into network design and operation. Let's get started!

## Installing containerlab

This script installs and starts Docker, a containerization platform, on a Linux machine using the dnf package manager. Then, it installs containerlab, a tool used for creating and managing container-based network labs. The command specified installs containerlab version 0.25.1. (it's for Fedora33)

```
# Install docker
sudo dnf -y install docker
sudo systemctl start docker
sudo systemctl enable docker

# Install containerlab
bash -c "$(curl -sL https://get.containerlab.dev)" -- -v 0.25.1
```

