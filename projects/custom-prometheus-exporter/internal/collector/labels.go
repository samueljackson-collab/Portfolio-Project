package collector

import (
	"fmt"
	"sort"
	"strings"
)

func mergeLabels(base, extra map[string]string) map[string]string {
	merged := map[string]string{}
	for key, value := range base {
		merged[key] = value
	}
	for key, value := range extra {
		merged[key] = value
	}
	return merged
}

func labelString(labels map[string]string) string {
	if len(labels) == 0 {
		return ""
	}
	keys := make([]string, 0, len(labels))
	for key := range labels {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	pairs := make([]string, 0, len(labels))
	for _, key := range keys {
		pairs = append(pairs, fmt.Sprintf("%s=%s", key, labels[key]))
	}
	return strings.Join(pairs, ",")
}
