# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Mock HLR/HSS implementation with subscriber database
- Location update state machine (Idle → Attached → Roaming → Detached)
- IMSI/MSISDN validation and generation utilities
- Roaming agreement validation logic
- Network selection algorithm
- Test scenarios for successful roaming
- Test scenarios for failed authentication
- Test scenarios for no roaming agreement
- Billing event trigger simulation
- SQLite subscriber database with sample data
- Configuration file for test scenarios
- Comprehensive test suite with pytest

### Security
- Synthetic IMSI/MSISDN generation (no real subscriber data)
- Test authentication key (Ki) generation
- Database encryption support

## [1.0.0] - 2024-11-07

### Added
- Initial project structure
- State machine engine
- Mock network components
