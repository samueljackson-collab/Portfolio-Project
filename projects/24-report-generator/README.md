# Project 24: Portfolio Report Generator

## Overview
Generates PDF/HTML status reports for the portfolio using Jinja2 templates and WeasyPrint.

## Run
```bash
pip install -r requirements.txt
python src/generate_report.py --template templates/weekly.html --output report.html
```


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Code Components

#### 1. Core Functionality
```
Create the main application logic for [specific feature], including error handling, logging, and configuration management
```

#### 2. API Integration
```
Generate code to integrate with [external service] API, including authentication, rate limiting, and retry logic
```

#### 3. Testing
```
Write comprehensive tests for [component], covering normal operations, edge cases, and error scenarios
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

