{{/*
Expand the name of the chart.
*/}}
{{- define "scrooge-mcduck.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "scrooge-mcduck.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "scrooge-mcduck.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "scrooge-mcduck.labels" -}}
helm.sh/chart: {{ include "scrooge-mcduck.chart" . }}
{{ include "scrooge-mcduck.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "scrooge-mcduck.selectorLabels" -}}
app.kubernetes.io/name: {{ include "scrooge-mcduck.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
GitLab annotations used for the Deploy boards feature.
*/}}
{{- define "scrooge-mcduck.gitlabAnnotations" -}}
app.gitlab.com/app: {{ .Values.global.gitlab.app }}
app.gitlab.com/env: {{ .Values.global.gitlab.env }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "scrooge-mcduck.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "scrooge-mcduck.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Reference a sub-chart template or function _in the context of that sub-chart_.
Shamelessly stolen from: https://github.com/helm/helm/issues/4535
*/}}
{{- define "call-nested" }}
{{- $dot := index . 0 }}
{{- $subchart := index . 1 }}
{{- $template := index . 2 }}
{{- include $template (dict "Chart" (dict "Name" $subchart) "Values" (index $dot.Values $subchart) "Release" $dot.Release "Capabilities" $dot.Capabilities) }}
{{- end }}
