{{- define "custom-prometheus-exporter.fullname" -}}
{{- printf "%s" .Release.Name -}}
{{- end -}}
