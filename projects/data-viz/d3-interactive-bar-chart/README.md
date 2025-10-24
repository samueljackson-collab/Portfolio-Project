# Interactive Bar Chart with D3.js

## Overview
A reusable data visualization component showcasing D3.js for interactive analytics dashboards. Demonstrates accessibility, responsiveness, and integration with React applications.

## Architecture
- Implemented as a standalone ES module with TypeScript types.
- Offers React wrapper component for direct usage inside the React To-Do analytics view.
- Supports data fetching via REST endpoints or local CSV/JSON.

## Features
- Animated transitions, tooltips, and keyboard navigation.
- Configurable color palettes using design tokens.
- Exposes events (`onBarClick`, `onFilterChange`) for parent app integrations.

## Usage
1. Install dependencies: `npm install`.
2. Run storybook for local development: `npm run storybook`.
3. Execute lint/tests: `npm run lint && npm run test`.
4. Build distributable package: `npm run build` (outputs to `dist/`).

## Quality & Documentation
- Storybook docs provide usage examples and accessibility notes.
- Visual regression tests with Chromatic.
- TypeDoc generates API documentation.

