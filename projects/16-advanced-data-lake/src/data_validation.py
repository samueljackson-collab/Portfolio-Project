"""Data validation framework for data lake pipelines."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

LOGGER = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation failures."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Overall validation status."""
    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    FAILED = "failed"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    rule_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    affected_rows: int = 0
    sample_failures: List[Any] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Complete validation report for a dataset."""
    dataset_name: str
    total_rows: int
    validation_time: datetime
    status: ValidationStatus
    results: List[ValidationResult]
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_rows": self.total_rows,
            "validation_time": self.validation_time.isoformat(),
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "summary": {
                "total_rules": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "warnings": sum(1 for r in self.results if r.severity == ValidationSeverity.WARNING),
                "errors": sum(1 for r in self.results if r.severity == ValidationSeverity.ERROR and not r.passed),
            },
            "results": [
                {
                    "rule_name": r.rule_name,
                    "passed": r.passed,
                    "severity": r.severity.value,
                    "message": r.message,
                    "affected_rows": r.affected_rows,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(
        self,
        name: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        description: str = "",
    ):
        self.name = name
        self.severity = severity
        self.description = description

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Execute the validation rule."""
        pass


class NotNullRule(ValidationRule):
    """Validates that a column has no null values."""

    def __init__(self, column: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(f"not_null_{column}", severity, f"Column {column} should not contain nulls")
        self.column = column

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if self.column not in df.columns:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Column {self.column} does not exist",
            )

        null_count = df[self.column].isna().sum()
        passed = null_count == 0

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Found {null_count} null values in {self.column}" if not passed else "No null values",
            affected_rows=int(null_count),
            details={"null_percentage": float(null_count / len(df) * 100) if len(df) > 0 else 0},
        )


class UniqueRule(ValidationRule):
    """Validates that a column contains unique values."""

    def __init__(self, column: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(f"unique_{column}", severity, f"Column {column} should contain unique values")
        self.column = column

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if self.column not in df.columns:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Column {self.column} does not exist",
            )

        duplicate_count = df[self.column].duplicated().sum()
        passed = duplicate_count == 0

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Found {duplicate_count} duplicate values in {self.column}" if not passed else "All values unique",
            affected_rows=int(duplicate_count),
        )


class RangeRule(ValidationRule):
    """Validates that numeric values fall within a range."""

    def __init__(
        self,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        super().__init__(f"range_{column}", severity, f"Column {column} values should be in range")
        self.column = column
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if self.column not in df.columns:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Column {self.column} does not exist",
            )

        violations = pd.Series([False] * len(df))

        if self.min_value is not None:
            violations |= df[self.column] < self.min_value
        if self.max_value is not None:
            violations |= df[self.column] > self.max_value

        violation_count = violations.sum()
        passed = violation_count == 0

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Found {violation_count} out-of-range values" if not passed else "All values in range",
            affected_rows=int(violation_count),
            details={"min": self.min_value, "max": self.max_value},
        )


class PatternRule(ValidationRule):
    """Validates that string values match a regex pattern."""

    def __init__(
        self,
        column: str,
        pattern: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        super().__init__(f"pattern_{column}", severity, f"Column {column} values should match pattern")
        self.column = column
        self.pattern = pattern

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if self.column not in df.columns:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Column {self.column} does not exist",
            )

        matches = df[self.column].astype(str).str.match(self.pattern, na=False)
        mismatch_count = (~matches).sum()
        passed = mismatch_count == 0

        sample_failures = df.loc[~matches, self.column].head(5).tolist()

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Found {mismatch_count} pattern mismatches" if not passed else "All values match pattern",
            affected_rows=int(mismatch_count),
            sample_failures=sample_failures,
            details={"pattern": self.pattern},
        )


class ReferentialIntegrityRule(ValidationRule):
    """Validates referential integrity between datasets."""

    def __init__(
        self,
        column: str,
        reference_values: set,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        super().__init__(f"referential_{column}", severity, f"Column {column} should reference valid values")
        self.column = column
        self.reference_values = reference_values

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        if self.column not in df.columns:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Column {self.column} does not exist",
            )

        invalid = ~df[self.column].isin(self.reference_values)
        invalid_count = invalid.sum()
        passed = invalid_count == 0

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Found {invalid_count} invalid references" if not passed else "All references valid",
            affected_rows=int(invalid_count),
            sample_failures=df.loc[invalid, self.column].head(5).tolist(),
        )


class CustomRule(ValidationRule):
    """Custom validation rule using a user-defined function."""

    def __init__(
        self,
        name: str,
        validator: Callable[[pd.DataFrame], tuple],
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ):
        super().__init__(name, severity, "Custom validation rule")
        self.validator = validator

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        passed, message, details = self.validator(df)

        return ValidationResult(
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details=details or {},
        )


class DataValidator:
    """Main data validation orchestrator."""

    def __init__(self):
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> "DataValidator":
        """Add a validation rule."""
        self.rules.append(rule)
        return self

    def add_not_null(self, column: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "DataValidator":
        return self.add_rule(NotNullRule(column, severity))

    def add_unique(self, column: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "DataValidator":
        return self.add_rule(UniqueRule(column, severity))

    def add_range(
        self,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "DataValidator":
        return self.add_rule(RangeRule(column, min_value, max_value, severity))

    def add_pattern(
        self,
        column: str,
        pattern: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
    ) -> "DataValidator":
        return self.add_rule(PatternRule(column, pattern, severity))

    def validate(self, df: pd.DataFrame, dataset_name: str = "dataset") -> ValidationReport:
        """Run all validation rules on the dataframe."""
        start_time = datetime.utcnow()
        results = []

        for rule in self.rules:
            try:
                result = rule.validate(df)
                results.append(result)
                LOGGER.info(f"Rule {rule.name}: {'PASSED' if result.passed else 'FAILED'}")
            except Exception as e:
                LOGGER.error(f"Rule {rule.name} execution failed: {e}")
                results.append(ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Rule execution failed: {e}",
                ))

        # Determine overall status
        has_errors = any(not r.passed and r.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for r in results)
        has_warnings = any(not r.passed and r.severity == ValidationSeverity.WARNING for r in results)

        if has_errors:
            status = ValidationStatus.FAILED
        elif has_warnings:
            status = ValidationStatus.PASSED_WITH_WARNINGS
        else:
            status = ValidationStatus.PASSED

        duration = (datetime.utcnow() - start_time).total_seconds()

        return ValidationReport(
            dataset_name=dataset_name,
            total_rows=len(df),
            validation_time=start_time,
            status=status,
            results=results,
            duration_seconds=duration,
        )


def create_bronze_validator() -> DataValidator:
    """Create standard validator for bronze layer data."""
    return (
        DataValidator()
        .add_not_null("event_id")
        .add_unique("event_id")
        .add_not_null("ingested_at")
    )


def create_silver_validator() -> DataValidator:
    """Create standard validator for silver layer data."""
    return (
        DataValidator()
        .add_not_null("event_id")
        .add_unique("event_id")
        .add_not_null("ingested_at")
        .add_not_null("status", severity=ValidationSeverity.WARNING)
    )
