replaces:
{{ $target := index .Vars .TargetName }}
{{- range $netinstances := index $target "network-instances" }}
  - path: "/tunnel-interface[name=vxlan2]/vxlan-interface[index={{ index $netinstances "vni" }}]"
    encoding: "json_ietf"
    value:
      type: bridged
      ingress:
        vni: {{ index $netinstances "vni" }}
{{- end }}
