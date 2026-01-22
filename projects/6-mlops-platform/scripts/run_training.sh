#!/bin/bash
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CONFIG_PATH=${1:-$PROJECT_ROOT/configs/churn-experiment.yaml}
TRACKING_URI=${MLFLOW_TRACKING_URI:-sqlite:///mlruns.db}

if [ ! -f "$CONFIG_PATH" ]; then
  echo "Configuration file not found: $CONFIG_PATH" >&2
  exit 1
fi

export CONFIG_PATH
export MLFLOW_TRACKING_URI="$TRACKING_URI"
PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}" python - <<'PYTHON'
import os
from pathlib import Path
from mlops_pipeline import ExperimentRunner, load_experiment_config

config = load_experiment_config(Path(os.environ['CONFIG_PATH']))
runner = ExperimentRunner(tracking_uri=os.environ["MLFLOW_TRACKING_URI"])
model_name = runner.run(config)
runner.promote_model(model_name, "Staging")
print(f"Registered model: {model_name}")
PYTHON
