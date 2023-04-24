# Segment Routing and Kubernetes Lab: SRv6 L3VPN Flexible Algoritms Demo

# Do not use it! still under development!

This lab is showing a demo of SRv6 on Nokia routers to signal both IGP’s shortest path and Algorithms with specific metric conditions (i.e. 10ms). All router network interfaces for transport are <b>using IPv6</b> and we are encapsulating IPv4 traffic. Additonally, we have emulated three locations using SRL swicthes for Kubernetes Clusters. And testing taffic between CNF Apps located at those different locations. 

One of the locations is emulating a small datacenter using a spine/leaf + border-leaf design. We have connected MetalLB speakers to the leaf swicthes to expose services directly at the border-leaf (BGP Load Balancer Service)

Objectives:
* Create a traffic-engineered path between CNF Apps located on different sites, that uses delay as a metric via Flex Algorithms
* Understand the benefits of SRv6 to simplify the network setup at CNF App level

Conditions:
* IGP Metrics: All IGP link metrics are 100
* Delay Metrics: All delay metrics are 10msec with the exception of the R3-R5 link, which is 15msec.
* We have created two different customers. Conditions of latency is only apply to one of them
* DC apps are exposed via Border Leaf using BGP policies and peering MetalLB speakers from Fabric Leaf to Kubernetes worker nodes.
* One node K8s clusters at every Edge Location


## Network Setup

See topology on the next image:

![Segment Routing SRvv6 l3vpn demo Containlerlab no ISIS Path](images/srv6-flexible-algorithms-metallb-kubernetes-containerlab-mau-nokia-topology-1.png)

Next images show the same with one option of the shortest path using ISIS.
![Segment Routing SRvv6 l3vpn demo Containlerlab with shortest ISIS Path](images/srv6-flexible-algorithms-metallb-kubernetes-containerlab-mau-nokia-topology-2.png)

![Segment Routing SRvv6 l3vpn demo Containlerlab with shortest ISIS Path](images/srv6-flexible-algorithms-metallb-kubernetes-containerlab-mau-nokia-topology-3.png)

## SRv6 with Flexible Algorithm
Segment Routing (SR) is applied to the IPv6 data plane using 128-bit SIDs and the SR routing header (SRH). The 128-bit SRv6 SID consists of a Locator, a Function, and an Argument.
* The Locator is encoded in the most significant bits of the SID. It is typically routable and leads to the node that instantiated the SID.
* The Function identifies a local endpoint behaviour, such as End, End.X, End.DT4 or End.DT2U.
The Locator is advertised into the IGP and is associated with an Algorithm. As a result, support for Flexible-Algorithm is inherited from day one, and a level of traffic engineering is possible without SRH overhead.
* Flex-Algo 128 SRv6 Locators: Alg128: 2001:db8:4502:n::/64 where n is Node-ID, so 1 is R1, 6 is R6 and 7 is R7

### Testing
We have cassowary http testers running from Ege1 as CNF Apps all the way to a Simple HTTP service at Edge2 and the Datacenter. The latter is exposing the service via Load Balancer.
The testing metrics are collected via pushgateway and collected via prometheus. There's a grafana instance to visualize the info

![Cassowary HTTP tests exposed via Grafana](images/grafana-prometheus-pushgateway-cassowary-http-test-segment-routing-srv6-containerlab.png)

### Customer and VPN information
L3VPN info and prefixes can be found in customer.yml file in this repo
How we take care of the rest of the info like service-id and route target and route distinguisher, it's using the info from every customer. Check next pictures
![Segment Routing SRvv6 l3vpn demo Containlerlab Naming Logic](images/srv6-flexible-algorithms-network-orchestration-mau-nokia-logic-1.png)

![Segment Routing SRvv6 l3vpn demo Containlerlab Naming Logic](images/srv6-flexible-algorithms-network-orchestration-mau-nokia-logic-2.png)

## MetalLB
Every K8s worker is peering directly to every leaf swicth at the datacenter
```
A:LEAF-DC-1# show network-instance kube-ipvrf protocols bgp neighbor
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "kube-ipvrf"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+--------------------+------------------------------+--------------------+-------+-----------+----------------+----------------+---------------+------------------------------+
|      Net-Inst      |             Peer             |       Group        | Flags |  Peer-AS  |     State      |     Uptime     |   AFI/SAFI    |        [Rx/Active/Tx]        |
+====================+==============================+====================+=======+===========+================+================+===============+==============================+
| kube-ipvrf         | 1.1.1.210                    | border             | S     | 65310     | established    | 1d:2h:26m:55s  | ipv4-unicast  | [0/0/12]                     |
| kube-ipvrf         | 192.168.101.101              | metallb-bgp        | D     | 65201     | established    | 1d:2h:28m:40s  | ipv4-unicast  | [1/1/11]                     |
+--------------------+------------------------------+--------------------+-------+-----------+----------------+----------------+---------------+------------------------------+
```

Then, everytime an app is exposed via Load Balancer service, the service IP is exposed directly in the border leaf like is showing bellow for 10.254.254.240

```
A:BORDER-DC# show network-instance kube-ipvrf route-table all
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance kube-ipvrf
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+-------------------------------+-------+------------+----------------------+----------------------+----------+---------+-------------------+-------------------+
|            Prefix             |  ID   | Route Type |     Route Owner      |      Best/Fib-       |  Metric  |  Pref   |  Next-hop (Type)  |     Next-hop      |
|                               |       |            |                      |     status(slot)     |          |         |                   |     Interface     |
+===============================+=======+============+======================+======================+==========+=========+===================+===================+
| 1.1.1.201/32                  | 0     | bgp-evpn   | bgp_evpn_mgr         | True/success         | 0        | 170     | 1.1.1.1           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 1.1.1.202/32                  | 0     | bgp-evpn   | bgp_evpn_mgr         | True/success         | 0        | 170     | 1.1.1.2           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 1.1.1.210/32                  | 8     | host       | net_inst_mgr         | True/success         | 0        | 0       | None (extract)    | None              |
| 10.1.4.0/24                   | 0     | bgp        | bgp_mgr              | True/success         | 0        | 170     | 10.6.4.1          | None              |
|                               |       |            |                      |                      |          |         | (indirect)        |                   |
| 10.6.4.0/24                   | 10    | local      | net_inst_mgr         | True/success         | 0        | 0       | 10.6.4.254        | irb1.1001         |
|                               |       |            |                      |                      |          |         | (direct)          |                   |
| 10.6.4.254/32                 | 10    | host       | net_inst_mgr         | True/success         | 0        | 0       | None (extract)    | None              |
| 10.6.4.255/32                 | 10    | host       | net_inst_mgr         | True/success         | 0        | 0       | None (broadcast)  | None              |
| 10.10.10.0/24                 | 0     | bgp        | bgp_mgr              | True/success         | 0        | 170     | 10.106.4.1        | None              |
|                               |       |            |                      |                      |          |         | (indirect)        |                   |
| 10.106.4.0/24                 | 11    | local      | net_inst_mgr         | True/success         | 0        | 0       | 10.106.4.254      | irb1.1002         |
|                               |       |            |                      |                      |          |         | (direct)          |                   |
| 10.106.4.254/32               | 11    | host       | net_inst_mgr         | True/success         | 0        | 0       | None (extract)    | None              |
| 10.106.4.255/32               | 11    | host       | net_inst_mgr         | True/success         | 0        | 0       | None (broadcast)  | None              |
| 10.254.254.240/32             | 0     | bgp-evpn   | bgp_evpn_mgr         | True/success         | 0        | 170     | 1.1.1.1           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  | None              |
|                               |       |            |                      |                      |          |         | 1.1.1.2           |                   |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 192.168.4.4/30                | 0     | bgp        | bgp_mgr              | True/success         | 0        | 170     | 10.6.4.1          | None              |
|                               |       |            |                      |                      |          |         | (indirect)        | None              |
|                               |       |            |                      |                      |          |         | 10.106.4.1        |                   |
|                               |       |            |                      |                      |          |         | (indirect)        |                   |
| 192.168.101.0/24              | 0     | bgp-evpn   | bgp_evpn_mgr         | False/success        | 0        | 170     | 1.1.1.1           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  | None              |
|                               |       |            |                      |                      |          |         | 1.1.1.2           |                   |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 192.168.101.0/24              | 9     | local      | net_inst_mgr         | True/success         | 0        | 0       | 192.168.101.1     | irb0.0            |
|                               |       |            |                      |                      |          |         | (direct)          |                   |
| 192.168.101.1/32              | 9     | host       | net_inst_mgr         | True/success         | 0        | 0       | None (extract)    | None              |
| 192.168.101.101/32            | 0     | bgp-evpn   | bgp_evpn_mgr         | True/success         | 0        | 170     | 1.1.1.1           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 192.168.101.102/32            | 0     | bgp-evpn   | bgp_evpn_mgr         | True/success         | 0        | 170     | 1.1.1.2           | None              |
|                               |       |            |                      |                      |          |         | (indirect/vxlan)  |                   |
| 192.168.101.255/32            | 9     | host       | net_inst_mgr         | True/success         | 0        | 0       | None (broadcast)  | None              |
+-------------------------------+-------+------------+----------------------+----------------------+----------+---------+-------------------+-------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 routes total                    : 19
IPv4 prefixes with active routes     : 18
IPv4 prefixes with active ECMP routes: 3
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--{ running }--[  ]--
```

Below you can see Apps exposed via Load Balancer services from the datacenter K8s cluster
```
[root]# kubectl get svc --context kind-datacenter
NAME         TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)          AGE
hello-lb     LoadBalancer   10.96.166.199   10.254.254.240   8080:30778/TCP   26h
kubernetes   ClusterIP      10.96.0.1       <none>           443/TCP          26h
```

## Requirements
Versions used are:
* containerlab 0.25.1
* vr-sros 22.5.R2 (requires license)

SROS image was created using [VR Network Lab](https://github.com/vrnetlab/vrnetlab)
IMPORTANT: vr-sos must be set as an image in docker to be pull directly by containerlab
```
# docker images | grep vr-sros
vr-sros                               22.5.R2                         f33cd7a3732a        3 months ago        965MB
```

## Overview

If you are new with container lab, we recommed to check the post regading [Nokia SROS in the manual](https://containerlab.dev/manual/kinds/vr-sros/)

## Setting the lab

Create Bridges to use for delay testing and trigger Algorithm 128.

```
brctl addbr R2-R4
brctl addbr R3-R5
ip link set R2-R4 up
ip link set R3-R5 up
```

## Install the required applications
You will need:
* docker
* containerlab
* golang
* kubectl

The following is an script to install those requirements in Fedora
```
#Install docker
dnf -y install docker
systemctl start docker
systemctl enable docker


# Install containerlab
bash -c "$(curl -sL https://get.containerlab.dev)"

# Install go
dnf update -y
curl -LO https://go.dev/dl/go1.17.8.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.17.8.linux-amd64.tar.gz
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
source ~/.bashrc
go version

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256) kubectl" | sha256sum --check



# Run the installation
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client

#Install kind
go install sigs.k8s.io/kind@v0.12.0

# Add go path to ~/.bash_profile

sed -i -e '$aexport GOROOT=/usr/local/go' ~/.bash_profile
sed -i -e '$aexport GOPATH=$HOME/go' ~/.bash_profile
sed -i -e '$aexport PATH=$GOPATH/bin:$GOROOT/bin:$PATH' ~/.bash_profile

# Install Helm
bash -c "$(curl -sL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3)"
```

## Pull required images for the apps
```
for image in { alpine:latest busybox:latest python:latest quay.io/metallb/speaker:v0.12.1 quay.io/metallb/controller:v0.12.1 rogerw/cassowary:v0.14.1 pinrojas/cassowary:0.33 prom/pushgateway:latest }; do docker pull $image; done
```

## Installing the lab
Use the following batch
```
## get into the directory
./lab_scripts.sh -S
```


Test connectivity (origin is 10.1.4.101 and destination is using 10.6.4.101)
```
# docker exec -ti clab-srv6-demo-origin1 ping 10.6.4.101
PING 10.6.4.101 (10.6.4.101): 56 data bytes
64 bytes from 10.6.4.101: seq=0 ttl=60 time=11.766 ms
64 bytes from 10.6.4.101: seq=1 ttl=60 time=8.953 ms
64 bytes from 10.6.4.101: seq=2 ttl=60 time=8.865 ms
64 bytes from 10.6.4.101: seq=3 ttl=60 time=8.695 ms
```

# Checking Router configurations

All router must be part of Algo128 to make it work
```
A:admin@R31# admin show configuration /configure router isis flexible-algorithms
    admin-state enable
    flex-algo 128 {
        participate true
        loopfree-alternate { }
        micro-loop-avoidance { }
    }

[/]
```

```
A:admin@R6# admin show configuration /configure routing-options
    flexible-algorithm-definitions {
        flex-algo "Flex-Algo-128" {
            admin-state enable
            description "Flex-Algo for Delay Metric"
            metric-type delay
        }
    }

[/]
A:admin@R6# admin show configuration /configure router isis flexible-algorithms
    admin-state enable
    flex-algo 128 {
        participate true
        advertise "Flex-Algo-128"
        loopfree-alternate { }
        micro-loop-avoidance { }
    }

[/]
```

Check ISIS database for validation:
```
A:admin@R31# show router isis database R31.00-00 level 1 detail | match "Router Cap" post-lines 10
  Router Cap : 192.0.2.31, D:0, S:0
    TE Node Cap : B E M  P
    SR Cap: IPv4 MPLS-IPv6
       SRGB Base:12000, Range:8000
    SR Alg: metric based SPF, 128
    Node MSD Cap: BMI : 12 ERLD : 15 SRH-MAX-SL : 10 SRH-MAX-END-POP : 9 SRH-MAX-H-ENCAPS : 1 SRH-MAX-END-D : 9
    SRv6 Cap: 0x0000
  I/F Addresses :
    I/F Address   : 192.0.2.31
    I/F Address   : 192.168.0.66
    I/F Address   : 192.168.0.73

[/]
```

```
A:admin@R6# show router isis database R6.00-00 level 1 detail | match "Router Cap" post-lines 12
  Router Cap : 192.0.2.6, D:0, S:0
    TE Node Cap : B E M  P
    SR Cap: IPv4 MPLS-IPv6
       SRGB Base:12000, Range:8000
    SR Alg: metric based SPF, 128
    Node MSD Cap: BMI : 12 ERLD : 15 SRH-MAX-SL : 10 SRH-MAX-END-POP : 9 SRH-MAX-H-ENCAPS : 1 SRH-MAX-END-D : 9
    SRv6 Cap: 0x0000
    FAD Sub-Tlv:
        Flex-Algorithm   : 128
        Metric-Type      : delay
        Calculation-Type : 0
        Priority         : 100
        Flags: M

[/]
```

## Dynamic link delay measurement and propagation
For simplification, all links have a static unidirectional link delay value of 10mSec (10000uSec), except the R3-R5 link which has a static delay of 15mSec (15000uSec). 
The exception is the link R2-R4, which uses dynamic link delay measurement using STAMP probes. Link delay is introduced using a virtual network emulator.


```
A:admin@R2# show test-oam link-measurement interface to_R4 detail

===============================================================================
Interface Link Measurement Information - to_R4
===============================================================================
Template Name: direct-link
Oper State               : Up
Protocol                 : IPv4
Oper Source Address      : 192.168.0.13
Source Auto-Assigned     : Yes
Oper Destination Address : 192.168.0.14
Destination Auto-Assigned: Yes
Failure Condition(s)     : None
Detectable Tx Error      : None

-------------------------------------------------------------------------------
Reporting
-------------------------------------------------------------------------------
Reporting Enabled          : Yes
Delay Measure Last Reported: 1136us
Timestamp                  : 2023/01/03 22:26:57
Triggered By               : SampleThresholdRelative

-------------------------------------------------------------------------------
Aggregate Sample Window Delay Measurement Detail       Currently Reporting: Avg
-------------------------------------------------------------------------------
End Timestamp (UTC)               State Count Min(us) Max(us) Avg(us) I  Result
-------------------------------------------------------------------------------
N/A                          InProgress     0       0       0       0 -       0
2023/01/03 22:26:57          SwReported     1       0       0       0 N       0
2023/01/03 22:26:47           Completed     1     856     856     856 Y     856
2023/01/03 22:26:37          SwReported     1       0       0       0 N       0
2023/01/03 22:26:27          SwReported     1       0       0       0 N       0
2023/01/03 22:26:17           Completed     1     879     879     879 Y     879
2023/01/03 22:26:07          SwReported     1       0       0       0 N       0
2023/01/03 22:25:57          SwReported     1       0       0       0 N       0
2023/01/03 22:25:47           Completed     1     853     853     853 Y     853
2023/01/03 22:25:37          SwReported     1       0       0       0 N       0
2023/01/03 22:25:27          SwReported     1       0       0       0 N       0
2023/01/03 22:25:17          SwReported     1       0       0       0 N       0
2023/01/03 22:25:07           Completed     1     841     841     841 Y     841
2023/01/03 22:24:57           Completed     1     811     811     811 Y     811
2023/01/03 22:24:47           Completed     1     866     866     866 Y     866
2023/01/03 22:24:37           Completed     1     870     870     870 Y     870
2023/01/03 22:24:27           Completed     1     850     850     850 Y     850
2023/01/03 22:24:17           Completed     1     949     949     949 Y     949
2023/01/03 22:24:07           Completed     1     834     834     834 Y     834
2023/01/03 22:23:57          SwReported     1       0       0       0 N       0

-------------------------------------------------------------------------------
Sample Window Delay Measurement Detail                 Currently Reporting: Avg
-------------------------------------------------------------------------------
End Timestamp (UTC)       State  Rcv/Snt  Min(us) Max(us) Avg(us) Err I  Result
-------------------------------------------------------------------------------
N/A                  InProgress    3/3          0       0       0   0 -       0
2023/01/03 22:26:57  SwReported    5/5        767    2417    1136   0 Y    1136
2023/01/03 22:26:47   Completed    5/5        758    1041     856   0 Y     856
2023/01/03 22:26:37  SwReported    5/5        700     960     856   0 Y     856
2023/01/03 22:26:27  SwReported    5/5        801    1496     987   0 Y     987
2023/01/03 22:26:17   Completed    5/5        746     972     879   0 Y     879
2023/01/03 22:26:07  SwReported    5/5        779     938     828   0 Y     828
2023/01/03 22:25:57  SwReported    5/5        808    1719    1055   0 Y    1055
```


These static/dynamic values are advertised into IS-IS.

```
A:admin@R2# show router isis database R2.00-00 level 2 detail | match "Nbr   : R4.00" post-lines 28
    Nbr   : R4.00
    Default Metric  : 100
    Sub TLV Len     : 137
    IF Addr   : 192.168.0.13
    Nbr IP    : 192.168.0.14
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:R S
        MaxLink BW: 10000000 kbps
        TE Metric : 20
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:R
        Resvble BW: 10000000 kbps
        Unresvd BW:
            BW[0] : 10000000 kbps
            BW[1] : 10000000 kbps
            BW[2] : 10000000 kbps
            BW[3] : 10000000 kbps
            BW[4] : 10000000 kbps
            BW[5] : 10000000 kbps
            BW[6] : 10000000 kbps
            BW[7] : 10000000 kbps
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:   X
        Admin Grp : 0x400
        Delay Min : 858 Max : 858
        TE Metric : 20
    Adj-SID: Flags:v4BVLP Weight:0 Label:20204
    Adj-SID: Flags:v6BVL Weight:0 Label:524285
    End.X-SID: 2001:db8:4501:2:0:4000:: flags:B algo:0 weight:0 endpoint:End.X-USP
```

## Verifying SRv6-ISIS tunnel

Check the route-table for tunnels
```
A:admin@R1# show router route-table ipv6 2001:db8:4502:6::/64

===============================================================================
IPv6 Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
2001:db8:4502:6::/64                          Remote  ISIS      00h00m02s  15
       2001:db8:4502:6::/64 (tunneled:SRV6-ISIS)                    40818
-------------------------------------------------------------------------------
No. of Routes: 1
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================

[/]
A:admin@R1# show router route-table ipv6 2001:db8:4502:7::/64

===============================================================================
IPv6 Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
2001:db8:4502:7::/64                          Remote  ISIS      00h00m07s  15
       2001:db8:4502:7::/64 (tunneled:SRV6-ISIS)                    40818
-------------------------------------------------------------------------------
No. of Routes: 1
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================

[/]
```

```
A:admin@R1# show router tunnel-table ipv6 2001:db8:4502:7::/64

===============================================================================
IPv6 Tunnel Table (Router: Base)
===============================================================================
Destination                                     Owner     Encap TunnelId  Pref
Nexthop                                         Color           Metric
-------------------------------------------------------------------------------
2001:db8:4502:7::/64 [L]                        srv6-isis SRV6  524304    0
  fe80::5054:ff:fe1c:9300-"to_R11"                                40795
-------------------------------------------------------------------------------
Flags: B = BGP or MPLS backup hop available
       L = Loop-Free Alternate (LFA) hop available
       E = Inactive best-external BGP route
       k = RIB-API or Forwarding Policy backup hop
===============================================================================

[/]
A:admin@R1# show router tunnel-table ipv6 2001:db8:4502:6::/64

===============================================================================
IPv6 Tunnel Table (Router: Base)
===============================================================================
Destination                                     Owner     Encap TunnelId  Pref
Nexthop                                         Color           Metric
-------------------------------------------------------------------------------
2001:db8:4502:6::/64 [L]                        srv6-isis SRV6  524303    0
  fe80::5054:ff:fe1c:9300-"to_R11"                                40795
-------------------------------------------------------------------------------
Flags: B = BGP or MPLS backup hop available
       L = Loop-Free Alternate (LFA) hop available
       E = Inactive best-external BGP route
       k = RIB-API or Forwarding Policy backup hop
===============================================================================

[/]
```

```
A:admin@R1# traceroute 2001:db8:4502:6:: source-address 2001:db8:4502:1::
traceroute to 2001:db8:4502:6:: from 2001:db8:4502:1::, 30 hops max, 60 byte packets
  1  2001:db8:33ad::2 (2001:db8:33ad::2)    3.86 ms  1.73 ms  1.73 ms
  2  2001:db8:33ad::12 (2001:db8:33ad::12)    3.72 ms  2.70 ms  2.39 ms
  3  2001:db8:33ad::e (2001:db8:33ad::e)    4.60 ms  5.17 ms  3.48 ms
  4  2001:db8:33ad::42 (2001:db8:33ad::42)    6.17 ms  5.42 ms  4.65 ms
  5  2001:db8:33ad::4d (2001:db8:33ad::4d)    6.16 ms  6.99 ms  6.38 ms
[/]
A:admin@R1# traceroute 2001:db8:4502:7:: source-address 2001:db8:4502:1::
traceroute to 2001:db8:4502:7:: from 2001:db8:4502:1::, 30 hops max, 60 byte packets
  1  2001:db8:33ad::2 (2001:db8:33ad::2)    2.34 ms  1.71 ms  1.49 ms
  2  2001:db8:33ad::12 (2001:db8:33ad::12)    2.86 ms  2.76 ms  2.88 ms
  3  2001:db8:33ad::e (2001:db8:33ad::e)    3.88 ms  3.58 ms  3.66 ms
  4  2001:db8:33ad::42 (2001:db8:33ad::42)    5.18 ms  5.48 ms  4.68 ms
  5  2001:db8:33ad::5e (2001:db8:33ad::5e)    6.86 ms  5.85 ms  8.93 ms
[/]
```
```
A:admin@R1# show router isis database R1.00-00 level 1 detail | match "SRv6 Locator" post-lines 10
  SRv6 Locator  :
    MT ID : 0
    Metric: ( ) 1 Algo:0
    Prefix   : 2001:db8:4501:1::/64
    Sub TLV   :
      AttrFlags: N
      End-SID   : 2001:db8:4501:1:0:1000::, flags:0x0, endpoint:End-USP
    Metric: ( ) 1 Algo:128
    Prefix   : 2001:db8:4502:1::/64
    Sub TLV   :
      AttrFlags: N

[/]
```

## Adding delay to R2-R4

```
# brctl show
bridge name	bridge id		STP enabled	interfaces
R2-R4		8000.7645097640f5	no		eth3
							eth4
# tc qdisc add dev eth3 root netem delay 40ms
```

```
A:admin@R2# show test-oam link-measurement interface to_R4 detail

===============================================================================
Interface Link Measurement Information - to_R4
===============================================================================
Template Name: direct-link
Oper State               : Up
Protocol                 : IPv4
Oper Source Address      : 192.168.0.13
Source Auto-Assigned     : Yes
Oper Destination Address : 192.168.0.14
Destination Auto-Assigned: Yes
Failure Condition(s)     : None
Detectable Tx Error      : None

-------------------------------------------------------------------------------
Reporting
-------------------------------------------------------------------------------
Reporting Enabled          : Yes
Delay Measure Last Reported: 20896us
Timestamp                  : 2023/01/03 22:48:17
Triggered By               : SampleThresholdRelative

-------------------------------------------------------------------------------
Aggregate Sample Window Delay Measurement Detail       Currently Reporting: Avg
-------------------------------------------------------------------------------
End Timestamp (UTC)               State Count Min(us) Max(us) Avg(us) I  Result
-------------------------------------------------------------------------------
N/A                          InProgress     0       0       0       0 -       0
2023/01/03 22:49:17           Completed     1   20857   20857   20857 Y   20857
2023/01/03 22:49:07           Completed     1   20814   20814   20814 Y   20814
2023/01/03 22:48:57           Completed     1   20829   20829   20829 Y   20829
2023/01/03 22:48:47           Completed     1   20808   20808   20808 Y   20808
2023/01/03 22:48:37           Completed     1   20842   20842   20842 Y   20842
2023/01/03 22:48:27           Completed     1   20819   20819   20819 Y   20819
```

```
A:admin@R2# show router isis database R2.00-00 level 2 detail | match "Nbr   : R4.00" post-lines 28
    Nbr   : R4.00
    Default Metric  : 100
    Sub TLV Len     : 137
    IF Addr   : 192.168.0.13
    Nbr IP    : 192.168.0.14
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:R S
        MaxLink BW: 10000000 kbps
        TE Metric : 20
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:R
        Resvble BW: 10000000 kbps
        Unresvd BW:
            BW[0] : 10000000 kbps
            BW[1] : 10000000 kbps
            BW[2] : 10000000 kbps
            BW[3] : 10000000 kbps
            BW[4] : 10000000 kbps
            BW[5] : 10000000 kbps
            BW[6] : 10000000 kbps
            BW[7] : 10000000 kbps
    TE APP LINK ATTR    :
      SABML-flag:Non-Legacy SABM-flags:   X
        Admin Grp : 0x400
        Delay Min : 20896 Max : 20896
        TE Metric : 20
    Adj-SID: Flags:v4BVLP Weight:0 Label:20204
    Adj-SID: Flags:v6BVL Weight:0 Label:524285
    End.X-SID: 2001:db8:4501:2:0:4000:: flags:B algo:0 weight:0 endpoint:End.X-USP
```

## Check changes in the route

The prefixes used for every locator (Algorithm)
* Alg0: 2001:db8:4501:6::
* Alg128: 2001:db8:4502:6::

Alg128 has change its path as you can see next

```
A:admin@R1# traceroute 2001:db8:4501:6:: source-address 2001:db8:4501:1::
traceroute to 2001:db8:4501:6:: from 2001:db8:4501:1::, 30 hops max, 60 byte packets
  1  2001:db8:33ad::2 (2001:db8:33ad::2)    3.55 ms  1.68 ms  1.77 ms
  2  2001:db8:33ad::12 (2001:db8:33ad::12)    3.66 ms  2.81 ms  2.60 ms
  3  2001:db8:33ad::e (2001:db8:33ad::e)    44.6 ms  43.9 ms  43.7 ms
  4  2001:db8:33ad::42 (2001:db8:33ad::42)    56.3 ms  44.9 ms  44.8 ms
  5  2001:db8:33ad::4d (2001:db8:33ad::4d)    49.5 ms  46.0 ms  45.6 ms
[/]
A:admin@R1# traceroute 2001:db8:4502:6:: source-address 2001:db8:4501:1::
traceroute to 2001:db8:4502:6:: from 2001:db8:4501:1::, 30 hops max, 60 byte packets
  1  2001:db8:33ad::6 (2001:db8:33ad::6)    2.92 ms  1.66 ms  4.37 ms
  2  2001:db8:33ad::a (2001:db8:33ad::a)    3.25 ms  2.78 ms  2.51 ms
  3  2001:db8:33ad::16 (2001:db8:33ad::16)    4.74 ms  3.67 ms  3.52 ms
  4  2001:db8:33ad::46 (2001:db8:33ad::46)    5.34 ms  4.44 ms  4.44 ms
  5  2001:db8:33ad::4d (2001:db8:33ad::4d)    47.9 ms  45.9 ms  46.5 ms
[/]
```

## Remove delay

```
# tc qdisc del dev eth3 root
# tc qdisc add dev eth3 root netem delay 20ms
```


## Other way to test Alg128

Start ping with some specific packet size from origin1 container
```
# docker exec -it clab-srv6-demo-origin1 ping -s 30000  10.6.4.101
PING 10.6.4.101 (10.6.4.101): 30000 data bytes
30008 bytes from 10.6.4.101: seq=0 ttl=60 time=98.014 ms
30008 bytes from 10.6.4.101: seq=1 ttl=60 time=98.423 ms
30008 bytes from 10.6.4.101: seq=2 ttl=60 time=98.280 ms
```
and container origin2
```
# docker exec -it clab-srv6-demo-origin2 ping -s 30000  10.6.4.101
PING 10.6.4.101 (10.6.4.101): 30000 data bytes
30008 bytes from 10.6.4.101: seq=0 ttl=60 time=69.702 ms
30008 bytes from 10.6.4.101: seq=1 ttl=60 time=59.359 ms
30008 bytes from 10.6.4.101: seq=2 ttl=60 time=56.598 ms
30008 bytes from 10.6.4.101: seq=3 ttl=60 time=56.455 ms
30008 bytes from 10.6.4.101: seq=4 ttl=60 time=56.266 ms
```
Check traffic in R3, adding and removing delay
```
A:admin@R3# monitor port 1/1/c5/1 rate

===============================================================================
Monitor statistics for Port 1/1/c5/1
===============================================================================
                                                   Input                 Output
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
At time t = 0 sec (Base Statistics)
-------------------------------------------------------------------------------
Octets                                            512702                 557512
Packets                                             1827                   2014
Errors                                                 0                      0

-------------------------------------------------------------------------------
At time t = 10 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                               167                    195
Packets                                                0                      1
Errors                                                 0                      0
Bits                                                1336                   1560
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 20 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                                27                     27
Packets                                                0                      0
Errors                                                 0                      0
Bits                                                 216                    216
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 30 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                               160                     43
Packets                                                0                      0
Errors                                                 0                      0
Bits                                                1280                    344
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 40 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                              9575                  15598
Packets                                                4                      6
Errors                                                 0                      0
Bits                                               76600                 124784
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 50 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30874                  30874
Packets                                               10                     10
Errors                                                 0                      0
Bits                                              246992                 246992
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 60 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30855                  30855
Packets                                               10                     10
Errors                                                 0                      0
Bits                                              246840                 246840
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 70 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30988                  30872
Packets                                               10                     10
Errors                                                 0                      0
Bits                                              247904                 246976
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 80 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             21765                  15599
Packets                                                7                      5
Errors                                                 0                      0
Bits                                              174120                 124792
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 90 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                               167                    167
Packets                                                0                      0
Errors                                                 0                      0
Bits                                                1336                   1336
Utilization (% of port capacity)                   ~0.00                  ~0.00
```

Check traffic in R2, adding and removing delay
(Only one app has been moved from one path to the other)

```
A:admin@R2# monitor port 1/1/c5/1 rate

===============================================================================
Monitor statistics for Port 1/1/c5/1
===============================================================================
                                                   Input                 Output
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
At time t = 0 sec (Base Statistics)
-------------------------------------------------------------------------------
Octets                                           4320418                4466953
Packets                                             5350                   5438
Errors                                                 0                      0

-------------------------------------------------------------------------------
At time t = 10 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30950                  30971
Packets                                               11                     11
Errors                                                 0                      0
Bits                                              247600                 247768
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 20 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             31090                  31090
Packets                                               11                     11
Errors                                                 0                      0
Bits                                              248720                 248720
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 30 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30969                  30969
Packets                                               11                     11
Errors                                                 0                      0
Bits                                              247752                 247752
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 40 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             30950                  30961
Packets                                               11                     11
Errors                                                 0                      0
Bits                                              247600                 247688
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 50 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             31143                  31109
Packets                                               12                     12
Errors                                                 0                      0
Bits                                              249144                 248872
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 60 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             40389                  58980
Packets                                               16                     21
Errors                                                 0                      0
Bits                                              323112                 471840
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 70 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             61945                  62073
Packets                                               22                     22
Errors                                                 0                      0
Bits                                              495560                 496584
Utilization (% of port capacity)                   ~0.00                  ~0.00

-------------------------------------------------------------------------------
At time t = 80 sec (Mode: Rate)
-------------------------------------------------------------------------------
Octets                                             61785                  61998
Packets                                               21                     22
Errors                                                 0                      0
Bits                                              494280                 495984
Utilization (% of port capacity)                   ~0.00                  ~0.00
```
