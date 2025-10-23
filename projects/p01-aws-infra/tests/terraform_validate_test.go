package tests

import (
	"os/exec"
	"path/filepath"
	"testing"
)

func TestTerraformValidateProd(t *testing.T) {
	t.Parallel()

	envDir, err := filepath.Abs("../infra/environments/prod")
	if err != nil {
		t.Fatalf("failed to resolve environment path: %v", err)
	}

	cmd := exec.Command("terraform", "init", "-backend=false", "-input=false")
	cmd.Dir = envDir
	if out, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("terraform init failed: %v\n%s", err, out)
	}

	validateCmd := exec.Command("terraform", "validate")
	validateCmd.Dir = envDir
	if out, err := validateCmd.CombinedOutput(); err != nil {
		t.Fatalf("terraform validate failed: %v\n%s", err, out)
	}
}
