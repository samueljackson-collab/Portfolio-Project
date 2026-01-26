# Runbook — Project 12 (Quantum Computing Integration)

## Overview

Production operations runbook for hybrid quantum-classical computing platform. This runbook covers quantum job management with Qiskit, AWS Batch orchestration, portfolio optimization workflows, fallback mechanisms, and monitoring for quantum computing operations.

**System Components:**
- Qiskit (quantum circuit design and execution)
- AWS Batch (classical job orchestration)
- IBM Quantum / Qiskit Runtime (quantum backend)
- Portfolio optimizer (VQE-based optimization)
- CloudWatch (metrics and monitoring)
- S3 (job results storage)
- Simulated annealing (classical fallback)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Quantum job success rate** | 90% | Successful quantum jobs / total jobs |
| **Job completion time (VQE)** | < 10 minutes | Time from submit → results ready |
| **Fallback activation rate** | < 20% | Classical fallback / total jobs |
| **Result accuracy** | > 95% | Solution quality vs known optimal |
| **Queue wait time** | < 5 minutes | Time in quantum backend queue |
| **AWS Batch job success** | 98% | Batch job completion rate |
| **Data persistence** | 100% | Results saved to S3 successfully |

---

## Dashboards & Alerts

### Dashboards

#### Quantum System Health
```bash
# Check IBM Quantum backend status
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backends = service.backends()
for backend in backends:
    print(f'{backend.name}: {backend.status().status_msg}')
"

# Check backend queue
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.backend('ibmq_qasm_simulator')
print(f'Pending jobs: {backend.status().pending_jobs}')
"

# Check available quantum credits
python src/check_quantum_credits.py
```

#### AWS Batch Dashboard
```bash
# Check Batch job queues
aws batch describe-job-queues

# Check compute environments
aws batch describe-compute-environments

# List recent jobs
aws batch list-jobs \
  --job-queue quantum-job-queue \
  --job-status RUNNING \
  --max-results 10

# Check job success rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Batch \
  --metric-name SuccessfulJobs \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

#### Portfolio Optimization Metrics
```bash
# Check recent optimization runs
aws s3 ls s3://quantum-results/portfolio-optimization/ --recursive | tail -20

# View optimization metrics
aws cloudwatch get-metric-statistics \
  --namespace QuantumComputing \
  --metric-name OptimizationQuality \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Minimum,Maximum

# Check fallback activation rate
aws cloudwatch get-metric-statistics \
  --namespace QuantumComputing \
  --metric-name ClassicalFallbackActivated \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Quantum backend unreachable | Immediate | Check IBM Quantum status, credentials |
| **P0** | All optimization jobs failing | Immediate | Enable fallback, investigate |
| **P1** | Quantum job queue > 50 | 30 minutes | Use classical fallback, request more backends |
| **P1** | AWS Batch compute unavailable | 30 minutes | Check EC2 capacity, scale compute env |
| **P1** | Fallback rate > 50% | 1 hour | Investigate quantum backend issues |
| **P2** | Job completion time > 20 min | 2 hours | Optimize circuits, check queue |
| **P2** | Result quality degraded | 2 hours | Review algorithm parameters |
| **P3** | Individual job failure | 4 hours | Review job logs, retry |

#### Alert Queries

```bash
# Check quantum backend connectivity
if ! python -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService().backends()" > /dev/null 2>&1; then
  echo "ALERT: Cannot connect to IBM Quantum backends"
  exit 1
fi

# Check job failure rate
FAILED_JOBS=$(aws batch list-jobs --job-queue quantum-job-queue --job-status FAILED --max-results 100 | jq '.jobSummaryList | length')
TOTAL_JOBS=$(aws batch list-jobs --job-queue quantum-job-queue --max-results 100 | jq '.jobSummaryList | length')

if [ $TOTAL_JOBS -gt 0 ]; then
  FAILURE_RATE=$(echo "scale=2; $FAILED_JOBS / $TOTAL_JOBS * 100" | bc)
  if [ $(echo "$FAILURE_RATE > 10" | bc) -eq 1 ]; then
    echo "ALERT: Job failure rate is ${FAILURE_RATE}%"
  fi
fi

# Check quantum queue length
QUEUE_LENGTH=$(python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.backend('ibmq_qasm_simulator')
print(backend.status().pending_jobs)
")

if [ "$QUEUE_LENGTH" -gt 50 ]; then
  echo "ALERT: Quantum backend queue length is $QUEUE_LENGTH"
fi

# Check results are being saved
RECENT_RESULTS=$(aws s3 ls s3://quantum-results/portfolio-optimization/ --recursive | \
  awk -v date="$(date -d '10 minutes ago' +%Y-%m-%d)" '$1 >= date' | wc -l)

if [ $RECENT_RESULTS -eq 0 ]; then
  echo "ALERT: No optimization results saved in last 10 minutes"
fi
```

---

## Standard Operations

### Quantum Backend Operations

#### Configure IBM Quantum Access
```bash
# Save IBM Quantum credentials
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='YOUR_IBM_QUANTUM_TOKEN',
    overwrite=True
)
"

# Verify access
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
print('Available backends:')
for backend in service.backends():
    print(f'  {backend.name}')
"

# List backend capabilities
python src/list_backend_capabilities.py
```

#### Select and Configure Backend
```bash
# Get least busy backend
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy

service = QiskitRuntimeService()
backends = service.backends(simulator=False, operational=True)
backend = least_busy(backends)
print(f'Least busy backend: {backend.name}')
print(f'Pending jobs: {backend.status().pending_jobs}')
"

# Use simulator for testing
export QUANTUM_BACKEND=ibmq_qasm_simulator

# Use real quantum hardware for production
export QUANTUM_BACKEND=ibm_nairobi

# Configure in application
vim config/quantum_config.yaml
```

#### Monitor Backend Status
```bash
# Check backend availability
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.backend('$QUANTUM_BACKEND')
status = backend.status()
print(f'Operational: {status.operational}')
print(f'Status: {status.status_msg}')
print(f'Pending jobs: {status.pending_jobs}')
"

# Check backend properties
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.backend('$QUANTUM_BACKEND')
config = backend.configuration()
print(f'Qubits: {config.n_qubits}')
print(f'Max experiments: {config.max_experiments}')
print(f'Max shots: {config.max_shots}')
"

# Monitor backend maintenance schedule
curl -s https://quantum-computing.ibm.com/services/resources/backends | jq .
```

### Portfolio Optimization Operations

#### Run Portfolio Optimization
```bash
# Single optimization run
cd /home/user/Portfolio-Project/projects/12-quantum-computing
source venv/bin/activate

python src/portfolio_optimizer.py \
  --stocks AAPL,GOOGL,MSFT,AMZN \
  --risk-tolerance 0.5 \
  --backend ibmq_qasm_simulator

# Run with custom parameters
python src/portfolio_optimizer.py \
  --config config/portfolio_config.json \
  --backend ibm_nairobi \
  --max-iterations 100 \
  --shots 1024

# Run in background
nohup python src/portfolio_optimizer.py \
  --stocks AAPL,GOOGL,MSFT,AMZN,TSLA \
  --risk-tolerance 0.3 \
  > logs/optimization_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

#### Submit AWS Batch Job
```bash
# Submit optimization job to AWS Batch
aws batch submit-job \
  --job-name portfolio-optimization-$(date +%Y%m%d-%H%M%S) \
  --job-queue quantum-job-queue \
  --job-definition quantum-portfolio-optimizer:1 \
  --parameters stocks="AAPL,GOOGL,MSFT",riskTolerance="0.5"

# Monitor job status
JOB_ID=$(aws batch list-jobs --job-queue quantum-job-queue --job-status RUNNING \
  --query 'jobSummaryList[0].jobId' --output text)
aws batch describe-jobs --jobs $JOB_ID

# View job logs
aws logs tail /aws/batch/job --follow

# Cancel job if needed
aws batch terminate-job --job-id $JOB_ID --reason "User requested cancellation"
```

#### Retrieve and Analyze Results
```bash
# List recent results
aws s3 ls s3://quantum-results/portfolio-optimization/ --recursive | tail -20

# Download specific result
RESULT_FILE="portfolio_optimization_20251110_143000.json"
aws s3 cp s3://quantum-results/portfolio-optimization/$RESULT_FILE results/

# Analyze results
python src/analyze_results.py --input results/$RESULT_FILE

# Compare quantum vs classical results
python src/compare_solutions.py \
  --quantum results/quantum_result.json \
  --classical results/classical_result.json

# Generate report
python src/generate_report.py --results-dir results/ --output report.html
```

### VQE Algorithm Management

#### Configure VQE Parameters
```bash
# Edit VQE configuration
vim config/vqe_config.yaml

# Example configuration:
cat > config/vqe_config.yaml << 'EOF'
vqe:
  ansatz: EfficientSU2
  optimizer: COBYLA
  max_iterations: 100
  initial_point: null

quantum:
  shots: 1024
  measurement_error_mitigation: true

convergence:
  tolerance: 1e-6
  max_evals: 1000

classical_fallback:
  enabled: true
  timeout_seconds: 600
  method: simulated_annealing
EOF

# Validate configuration
python src/validate_vqe_config.py config/vqe_config.yaml
```

#### Optimize Circuit Design
```bash
# Analyze circuit depth
python -c "
from qiskit import QuantumCircuit
from src.portfolio_optimizer import create_portfolio_circuit

circuit = create_portfolio_circuit(n_assets=4, risk_tolerance=0.5)
print(f'Circuit depth: {circuit.depth()}')
print(f'Gate count: {circuit.count_ops()}')
print(f'Qubits: {circuit.num_qubits}')
"

# Transpile circuit for target backend
python -c "
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService
from src.portfolio_optimizer import create_portfolio_circuit

service = QiskitRuntimeService()
backend = service.backend('ibm_nairobi')
circuit = create_portfolio_circuit(n_assets=4, risk_tolerance=0.5)
transpiled = transpile(circuit, backend=backend, optimization_level=3)
print(f'Original depth: {circuit.depth()}')
print(f'Transpiled depth: {transpiled.depth()}')
"

# Visualize circuit
python src/visualize_circuit.py --assets 4 --output circuit.png
```

### AWS Batch Management

#### Configure Compute Environment
```bash
# Create compute environment
aws batch create-compute-environment \
  --compute-environment-name quantum-compute-env \
  --type MANAGED \
  --compute-resources '{
    "type": "EC2",
    "minvCpus": 0,
    "maxvCpus": 256,
    "desiredvCpus": 4,
    "instanceTypes": ["optimal"],
    "subnets": ["subnet-12345"],
    "securityGroupIds": ["sg-12345"],
    "instanceRole": "arn:aws:iam::ACCOUNT:instance-profile/ecsInstanceRole"
  }'

# Update compute environment
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --compute-resources maxvCpus=512

# Disable compute environment
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state DISABLED
```

#### Manage Job Queues
```bash
# Create job queue
aws batch create-job-queue \
  --job-queue-name quantum-job-queue \
  --priority 100 \
  --compute-environment-order order=1,computeEnvironment=quantum-compute-env

# Update job queue priority
aws batch update-job-queue \
  --job-queue quantum-job-queue \
  --priority 200

# View queue status
aws batch describe-job-queues --job-queues quantum-job-queue

# List jobs in queue
aws batch list-jobs --job-queue quantum-job-queue --job-status RUNNABLE
aws batch list-jobs --job-queue quantum-job-queue --job-status RUNNING
```

#### Manage Job Definitions
```bash
# Register job definition
aws batch register-job-definition \
  --job-definition-name quantum-portfolio-optimizer \
  --type container \
  --container-properties '{
    "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/quantum-optimizer:latest",
    "vcpus": 4,
    "memory": 8192,
    "jobRoleArn": "arn:aws:iam::ACCOUNT:role/QuantumJobRole",
    "environment": [
      {"name": "QISKIT_IBM_TOKEN", "value": "TOKEN"},
      {"name": "RESULTS_BUCKET", "value": "quantum-results"}
    ]
  }'

# Update job definition (creates new revision)
aws batch register-job-definition \
  --job-definition-name quantum-portfolio-optimizer \
  --type container \
  --container-properties file://job-definition.json

# Deregister old revision
aws batch deregister-job-definition \
  --job-definition quantum-portfolio-optimizer:1
```

### Classical Fallback Operations

#### Configure Fallback Mechanism
```bash
# Edit fallback configuration
vim config/fallback_config.yaml

# Configuration:
cat > config/fallback_config.yaml << 'EOF'
fallback:
  enabled: true
  trigger_conditions:
    - quantum_backend_unavailable
    - queue_length_exceeds: 100
    - job_timeout_seconds: 600

  classical_method: simulated_annealing

  simulated_annealing:
    initial_temperature: 1000
    cooling_rate: 0.95
    iterations: 10000

  notification:
    enabled: true
    channels: [cloudwatch, email]
EOF

# Test fallback mechanism
python src/test_fallback.py --simulate-quantum-failure
```

#### Force Classical Execution
```bash
# Run with classical solver only
python src/portfolio_optimizer.py \
  --stocks AAPL,GOOGL,MSFT \
  --solver classical \
  --method simulated_annealing

# Compare performance
python src/benchmark_solvers.py \
  --stocks AAPL,GOOGL,MSFT,AMZN,TSLA \
  --iterations 10 \
  --output benchmark_results.json
```

---

## Incident Response

### Detection

**Automated Detection:**
- CloudWatch alarms for job failures
- Quantum backend status monitoring
- AWS Batch job queue alerts
- Result storage failures

**Manual Detection:**
```bash
# Check system health
./scripts/health_check.sh

# Check quantum backend status
python src/check_quantum_status.py

# Check recent job failures
aws batch list-jobs --job-queue quantum-job-queue --job-status FAILED --max-results 20

# Check logs for errors
aws logs tail /aws/batch/job --since 30m | grep -i error
tail -100 logs/portfolio_optimizer.log | grep -i error
```

### Triage

#### Severity Classification

### P0: Complete Service Failure
- All quantum backends unreachable
- AWS Batch compute environment down
- All optimization jobs failing
- Classical fallback also failing

### P1: Degraded Service
- Quantum backend unavailable (fallback working)
- AWS Batch jobs stuck in queue
- High job failure rate (> 25%)
- Results not being saved to S3

### P2: Performance Issues
- High quantum queue wait times
- Slow job completion
- Degraded result quality
- Intermittent backend connectivity

### P3: Minor Issues
- Individual job failure
- Non-critical algorithm warnings
- Monitoring gaps

### Incident Response Procedures

#### P0: All Optimization Jobs Failing

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check quantum backend status
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
try:
    backends = service.backends()
    print('Quantum backends accessible')
except Exception as e:
    print(f'ERROR: {e}')
"

# 2. Check AWS Batch status
aws batch describe-compute-environments \
  --compute-environments quantum-compute-env

# 3. Enable classical fallback immediately
export FORCE_CLASSICAL_FALLBACK=true
python src/portfolio_optimizer.py --solver classical

# 4. Check recent job logs
aws batch list-jobs --job-queue quantum-job-queue \
  --job-status FAILED --max-results 5 | \
  jq '.jobSummaryList[0].jobId' | \
  xargs -I {} aws batch describe-jobs --jobs {}

# 5. Notify team
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:quantum-alerts \
  --message "P0: All quantum optimization jobs failing"
```

**Investigation (5-20 minutes):**
```bash
# Check IBM Quantum service status
curl -s https://quantum-computing.ibm.com/api/status | jq .

# Check AWS Batch compute capacity
aws batch describe-compute-environments | \
  jq '.computeEnvironments[] | {name, state, status}'

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Batch \
  --metric-name FailedJobs \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:role/QuantumJobRole \
  --action-names s3:PutObject batch:SubmitJob \
  --resource-arns "*"

# Review application logs
tail -200 logs/portfolio_optimizer.log
```

**Recovery:**
```bash
# If quantum backend issue, switch to fallback
cat > config/runtime_override.yaml << 'EOF'
solver: classical
method: simulated_annealing
EOF

# If AWS Batch issue, restart compute environment
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state DISABLED

sleep 60

aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state ENABLED

# If credentials expired, refresh
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='NEW_TOKEN',
    overwrite=True
)
"

# Resubmit failed jobs
aws batch list-jobs --job-queue quantum-job-queue --job-status FAILED | \
  jq -r '.jobSummaryList[].jobName' | \
  while read jobname; do
    aws batch submit-job --job-name "$jobname-retry" \
      --job-queue quantum-job-queue \
      --job-definition quantum-portfolio-optimizer:latest
  done

# Verify recovery
python src/test_end_to_end.py
```

#### P1: Quantum Backend Queue Overloaded

**Investigation:**
```bash
# Check queue length across backends
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
for backend in service.backends(simulator=False, operational=True):
    status = backend.status()
    print(f'{backend.name}: {status.pending_jobs} pending jobs')
"

# Check our job positions
python src/check_job_queue_position.py

# Estimate wait time
python src/estimate_queue_wait.py
```

**Mitigation:**
```bash
# Switch to less busy backend
LEAST_BUSY=$(python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.providers.ibmq import least_busy
service = QiskitRuntimeService()
backends = service.backends(simulator=False, operational=True)
print(least_busy(backends).name)
")

echo "Switching to $LEAST_BUSY"
export QUANTUM_BACKEND=$LEAST_BUSY

# Activate classical fallback for non-critical jobs
python src/portfolio_optimizer.py \
  --solver auto \
  --fallback-threshold 50 \
  --max-queue-wait 300

# Request additional quantum time
# Contact IBM Quantum support for priority access

# Scale up classical processing
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --compute-resources maxvCpus=512
```

#### P1: Results Not Saving to S3

**Investigation:**
```bash
# Check S3 bucket accessibility
aws s3 ls s3://quantum-results/

# Test S3 write permissions
echo "test" | aws s3 cp - s3://quantum-results/test.txt
aws s3 rm s3://quantum-results/test.txt

# Check IAM role permissions
aws iam get-role-policy \
  --role-name QuantumJobRole \
  --policy-name S3AccessPolicy

# Review application logs for S3 errors
grep -i "s3\|boto" logs/portfolio_optimizer.log | tail -50
```

**Recovery:**
```bash
# Update IAM policy if needed
aws iam put-role-policy \
  --role-name QuantumJobRole \
  --policy-name S3AccessPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::quantum-results/*"
    }]
  }'

# Verify bucket region
aws s3api get-bucket-location --bucket quantum-results

# If region mismatch, update configuration
vim config/aws_config.yaml

# Manually upload cached results
for file in cache/*.json; do
  aws s3 cp $file s3://quantum-results/portfolio-optimization/
done
```

#### P2: Degraded Result Quality

**Investigation:**
```bash
# Analyze recent results
python src/analyze_result_quality.py \
  --start-date $(date -d '24 hours ago' +%Y-%m-%d) \
  --threshold 0.95

# Compare against benchmarks
python src/compare_to_benchmarks.py \
  --results results/recent/ \
  --benchmarks benchmarks/

# Check VQE convergence
grep "converged" logs/portfolio_optimizer.log | tail -20

# Review algorithm parameters
cat config/vqe_config.yaml
```

**Mitigation:**
```bash
# Increase VQE iterations
vim config/vqe_config.yaml
# max_iterations: 200

# Use better ansatz
vim config/vqe_config.yaml
# ansatz: RealAmplitudes  # or TwoLocal

# Increase shots for better statistics
export VQE_SHOTS=2048

# Enable error mitigation
vim config/vqe_config.yaml
# measurement_error_mitigation: true

# Rerun with updated parameters
python src/portfolio_optimizer.py \
  --config config/vqe_config.yaml \
  --stocks AAPL,GOOGL,MSFT,AMZN

# Verify improvement
python src/analyze_result_quality.py --latest
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/quantum-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Quantum Computing Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 2 hours
**Component:** IBM Quantum backend access

## Timeline
- 14:00: Jobs started failing with authentication errors
- 14:05: Confirmed quantum backend unreachable
- 14:10: Enabled classical fallback
- 14:30: Identified expired API token
- 14:45: Updated token and resubmitted jobs
- 16:00: All jobs completed successfully

## Root Cause
IBM Quantum API token expired and auto-renewal failed

## Action Items
- [ ] Implement token expiration monitoring
- [ ] Add automated token renewal
- [ ] Improve fallback activation logging
- [ ] Create token rotation runbook

EOF

# Update monitoring
aws cloudwatch put-metric-alarm \
  --alarm-name quantum-backend-connectivity \
  --alarm-description "Alert when quantum backend unreachable" \
  --metric-name QuantumBackendHealthCheck \
  --namespace QuantumComputing \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2

# Update documentation
echo "$(date +%Y-%m-%d): Updated quantum backend authentication procedure" >> CHANGELOG.md
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Backend not found" Error

**Symptoms:**
```bash
$ python src/portfolio_optimizer.py
Error: Backend 'ibm_lagos' not found
```

**Diagnosis:**
```bash
# List available backends
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
print('Available backends:')
for backend in service.backends():
    print(f'  {backend.name}')
"

# Check backend name in configuration
grep backend config/quantum_config.yaml
```

**Solution:**
```bash
# Update to valid backend name
vim config/quantum_config.yaml
# backend: ibmq_qasm_simulator

# Or use auto-selection
vim config/quantum_config.yaml
# backend: auto  # Will select least busy

# Verify
python src/portfolio_optimizer.py --dry-run
```

---

#### Issue: VQE Not Converging

**Symptoms:**
- Jobs complete but with poor results
- High objective function values
- Warning: "VQE did not converge"

**Diagnosis:**
```bash
# Check convergence metrics
grep -A 5 "VQE convergence" logs/portfolio_optimizer.log

# Analyze iteration history
python src/plot_convergence.py --log logs/portfolio_optimizer.log

# Check circuit characteristics
python -c "
from src.portfolio_optimizer import create_portfolio_circuit
circuit = create_portfolio_circuit(n_assets=5, risk_tolerance=0.5)
print(f'Circuit depth: {circuit.depth()}')
print(f'Circuit size too large for backend: {circuit.depth() > 100}')
"
```

**Solution:**
```bash
# Increase iteration limit
vim config/vqe_config.yaml
# max_iterations: 500

# Use better optimizer
vim config/vqe_config.yaml
# optimizer: SLSQP  # Instead of COBYLA

# Provide better initial point
python src/compute_initial_point.py --assets 5 > config/initial_point.json
vim config/vqe_config.yaml
# initial_point: config/initial_point.json

# Reduce problem size
python src/portfolio_optimizer.py \
  --stocks AAPL,GOOGL,MSFT  # Instead of 10 stocks

# Use adaptive ansatz depth
vim config/vqe_config.yaml
# ansatz_reps: auto  # Adaptive based on problem size

# Retry with new settings
python src/portfolio_optimizer.py --config config/vqe_config.yaml
```

---

#### Issue: AWS Batch Job Stuck in RUNNABLE

**Symptoms:**
- Job submitted but never starts
- Status remains RUNNABLE indefinitely

**Diagnosis:**
```bash
# Check compute environment status
aws batch describe-compute-environments \
  --compute-environments quantum-compute-env | \
  jq '.computeEnvironments[0] | {state, status, statusReason}'

# Check EC2 capacity
aws ec2 describe-instances \
  --filters "Name=tag:aws:batch:compute-environment,Values=quantum-compute-env" | \
  jq '.Reservations[].Instances[] | {InstanceId, State}'

# Check job requirements vs available capacity
aws batch describe-jobs --jobs $JOB_ID | \
  jq '.jobs[0] | {vcpus: .container.vcpus, memory: .container.memory}'

# Check for resource limits
aws service-quotas list-service-quotas \
  --service-code batch | \
  grep -i "vCPU\|instance"
```

**Solution:**
```bash
# If compute environment disabled, enable it
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state ENABLED

# If insufficient capacity, scale up
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --compute-resources maxvCpus=512,desiredvCpus=32

# If spot instance interruption, use on-demand
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --compute-resources type=EC2

# Resubmit job with lower resource requirements
aws batch submit-job \
  --job-name portfolio-optimization-reduced \
  --job-queue quantum-job-queue \
  --job-definition quantum-portfolio-optimizer:1 \
  --container-overrides vcpus=2,memory=4096
```

---

#### Issue: Classical Fallback Not Activating

**Symptoms:**
- Quantum backend unavailable
- Jobs timing out instead of falling back

**Diagnosis:**
```bash
# Check fallback configuration
cat config/fallback_config.yaml

# Check fallback logic in code
grep -A 10 "classical_fallback" src/portfolio_optimizer.py

# Test fallback manually
python src/test_fallback.py --force
```

**Solution:**
```bash
# Enable fallback if disabled
vim config/fallback_config.yaml
# enabled: true

# Lower trigger threshold
vim config/fallback_config.yaml
# trigger_conditions:
#   queue_length_exceeds: 50  # Lower from 100
#   job_timeout_seconds: 300  # Lower from 600

# Test fallback mechanism
python src/portfolio_optimizer.py \
  --force-fallback \
  --test-mode

# If code issue, update fallback logic
vim src/portfolio_optimizer.py
# Add more robust error handling

# Verify fallback works
python -c "
from src.portfolio_optimizer import PortfolioOptimizer
optimizer = PortfolioOptimizer(force_classical=True)
result = optimizer.optimize(['AAPL', 'GOOGL'])
print(f'Fallback result: {result}')
"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 24 hours (job results backup)
- **RTO** (Recovery Time Objective): 2 hours (resubmit jobs)

### Backup Strategy

**Results Backup:**
```bash
# Backup S3 results to archive
aws s3 sync s3://quantum-results/ s3://quantum-results-archive/

# Enable S3 versioning
aws s3api put-bucket-versioning \
  --bucket quantum-results \
  --versioning-configuration Status=Enabled

# Set up lifecycle policy for archival
aws s3api put-bucket-lifecycle-configuration \
  --bucket quantum-results \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "ArchiveOldResults",
      "Status": "Enabled",
      "Transitions": [{
        "Days": 90,
        "StorageClass": "GLACIER"
      }]
    }]
  }'

# Daily backup script
cat > /etc/cron.daily/quantum-backup << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
aws s3 sync s3://quantum-results/ s3://quantum-results-archive/$DATE/
find /var/log/quantum/ -name "*.log" -mtime -1 -exec gzip {} \;
EOF
chmod +x /etc/cron.daily/quantum-backup
```

**Configuration Backup:**
```bash
# Backup all configurations
tar czf quantum-config-backup-$(date +%Y%m%d).tar.gz \
  config/ \
  src/ \
  infrastructure/

# Store in S3
aws s3 cp quantum-config-backup-$(date +%Y%m%d).tar.gz \
  s3://quantum-backups/config/

# Backup AWS Batch configurations
aws batch describe-job-definitions > backup/job-definitions.json
aws batch describe-job-queues > backup/job-queues.json
aws batch describe-compute-environments > backup/compute-envs.json

# Git commit
git add -A
git commit -m "backup: quantum computing configurations $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

#### Complete AWS Infrastructure Loss

**Recovery Steps (2-4 hours):**
```bash
# 1. Restore from Git repository
git clone https://github.com/org/quantum-computing-platform.git
cd quantum-computing-platform

# 2. Deploy infrastructure with Terraform
cd infrastructure/
terraform init
terraform apply -auto-approve

# 3. Restore configurations
aws s3 cp s3://quantum-backups/config/latest.tar.gz .
tar xzf latest.tar.gz

# 4. Recreate AWS Batch resources
./scripts/setup_batch_environment.sh

# 5. Verify quantum backend access
python -c "
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
print('Backends:', [b.name for b in service.backends()])
"

# 6. Resubmit recent jobs (last 24 hours)
python scripts/resubmit_recent_jobs.py --since 24h

# 7. Verify system
./scripts/test_end_to_end.sh
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check quantum backend availability
python src/check_quantum_status.py

# Review job success rate
aws batch list-jobs --job-queue quantum-job-queue \
  --job-status SUCCEEDED --max-results 100 | jq '.jobSummaryList | length'

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace QuantumComputing \
  --metric-name JobSuccessRate \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average

# Review logs for errors
tail -100 logs/portfolio_optimizer.log | grep -i "error\|warning"
```

### Weekly Tasks
```bash
# Analyze result quality trends
python src/analyze_weekly_quality.py --output reports/weekly_quality.html

# Review costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=SERVICE \
  --filter file://quantum-cost-filter.json

# Clean up old results
aws s3 rm s3://quantum-results/ \
  --recursive \
  --exclude "*" \
  --include "*.json" \
  --older-than 30days

# Update dependencies
pip list --outdated
pip install --upgrade qiskit qiskit-ibm-runtime
```

### Monthly Tasks
```bash
# Review and optimize VQE parameters
python src/parameter_tuning.py --iterations 100 --output tuning_report.json

# Benchmark classical vs quantum performance
python src/benchmark_monthly.py --output benchmarks/$(date +%Y%m).json

# Review quantum credits usage
python src/check_quantum_credits.py --detailed

# Update IBM Quantum access tokens
python src/rotate_quantum_tokens.py

# Infrastructure review
cd infrastructure/
terraform plan

# Security audit
aws iam get-role-policy --role-name QuantumJobRole --policy-name S3AccessPolicy
./scripts/security_audit.sh
```

---

## Quick Reference

### Most Common Operations
```bash
# Run portfolio optimization
python src/portfolio_optimizer.py --stocks AAPL,GOOGL,MSFT --risk-tolerance 0.5

# Check quantum backend status
python src/check_quantum_status.py

# Submit AWS Batch job
aws batch submit-job --job-name opt-$(date +%s) \
  --job-queue quantum-job-queue \
  --job-definition quantum-portfolio-optimizer:latest

# View results
aws s3 ls s3://quantum-results/portfolio-optimization/ | tail -5

# Force classical fallback
python src/portfolio_optimizer.py --solver classical

# Check job status
aws batch list-jobs --job-queue quantum-job-queue --job-status RUNNING
```

### Emergency Response
```bash
# P0: All jobs failing - Enable fallback
export FORCE_CLASSICAL_FALLBACK=true
python src/portfolio_optimizer.py --solver classical

# P1: Quantum backend unavailable
python src/check_quantum_status.py
# Switch to alternative backend or use classical

# P1: AWS Batch stuck
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state DISABLED
aws batch update-compute-environment \
  --compute-environment quantum-compute-env \
  --state ENABLED

# P2: Poor result quality
vim config/vqe_config.yaml  # Increase iterations, change optimizer
python src/portfolio_optimizer.py --config config/vqe_config.yaml
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Quantum Computing Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
