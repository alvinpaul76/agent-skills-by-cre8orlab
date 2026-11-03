{{- with secret "<project-id>" "<env>" "/" -}}
{{- range . -}}
{{- if or (eq .Key "KEY_ONE") (eq .Key "KEY_TWO") -}}
{{ .Key }}={{ .Value }}
{{ end -}}
{{- end -}}
{{- end }}
# render-complete
