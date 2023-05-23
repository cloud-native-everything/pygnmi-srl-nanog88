replaces:
{{ $target := index .Vars .TargetName }}
{{- range $netinstances := index $target "network-instances" }}
  - path: "/network-instance[name={{ index $netinstances "name" }}]"
    encoding: "json_ietf"
    value: 
      admin-state: {{ index $netinstances "admin-state" | default "disable" }}
      type: {{ index $netinstances "type" | default "mac-vrf" }}
      description: {{ index $netinstances "description" | default "whatever" }}
{{- end }}
