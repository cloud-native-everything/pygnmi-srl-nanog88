## Example CLI usage

```
gnmic -a 172.18.100.122:57400 -u admin -p admin --skip-verify get -e json_ietf get --path /system/name/host-name
gnmic -a 172.18.100.122:57400 -u admin -p admin --skip-verify  set --request-file l2-domains.yml
gnmic -a clab-dc-k8s-LEAF-DC-1,clab-dc-k8s-LEAF-DC-2 -u admin -p admin --skip-verify set --request-vars l2-evpn-domains-create-vars.yml --request-file l2-evpn-domains-create.gotmpl
```
