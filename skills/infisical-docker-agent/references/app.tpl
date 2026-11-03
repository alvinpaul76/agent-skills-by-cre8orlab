{{- with secret "__INFISICAL_PROJECT_ID__" "__INFISICAL_ENV__" "/" -}}
{{- range . -}}
{{- if or (eq .Key "KEY_ONE") (eq .Key "KEY_TWO") -}}
{{ .Key }}={{ .Value }}
{{ end -}}
{{- end -}}
{{- end }}
# render-complete
