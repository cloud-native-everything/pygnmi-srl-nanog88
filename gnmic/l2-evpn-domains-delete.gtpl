deletes:
{{ $target := index .Vars .TargetName }}
{{- range $netinstances := index $target "network-instances" }}
  - "/network-instance[name={{ index $netinstances "name" }}]"
{{- end }}
