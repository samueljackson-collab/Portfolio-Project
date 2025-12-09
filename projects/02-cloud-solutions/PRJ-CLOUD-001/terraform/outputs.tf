output "solution_flag_path" {
  description = "Path to the feature flag parameter"
  value       = aws_ssm_parameter.solution_flag.name
}
