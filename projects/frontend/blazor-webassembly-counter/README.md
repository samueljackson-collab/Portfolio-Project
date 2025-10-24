# Blazor WebAssembly Counter Component

## Overview
C# Blazor WebAssembly component demonstrating modern .NET client-side development with shared state, API integration, and testing.

## Features
- Counter widget that synchronizes with backend via SignalR for multi-user updates.
- Uses .NET 8, dependency injection, and strongly-typed HTTP clients.
- Supports localization, dark mode, and adaptive layouts.

## Development Workflow
1. Install .NET SDK 8.0.
2. Run `dotnet restore` and `dotnet build`.
3. Start development server: `dotnet watch run` within `src/`.
4. Execute unit tests: `dotnet test` for component/unit tests (bUnit) and integration tests.

## Deployment
- Published as static assets served via S3/CloudFront (reuse Terraform module).
- Integrated into React app as micro-frontend via iframe or Web Component wrapper.

## Quality & Ops
- Analyzers (`StyleCop`, `FxCop`) enforce coding standards.
- GitHub Actions pipeline runs tests, publishes artifacts, and pushes to package feed.
- Observability via Application Insights for client telemetry.

