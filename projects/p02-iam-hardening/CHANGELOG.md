# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Least-privilege IAM policy for developer role
- Policy diff tool for change review
- IAM policy validation in Makefile
- Policy simulation capabilities
- Pytest test suite for policy compliance
- Documentation (README, HANDBOOK)

### Security
- Explicit deny for production resources in developer policy
- S3 access scoped to dev buckets only
- No IAM modification permissions in developer role
