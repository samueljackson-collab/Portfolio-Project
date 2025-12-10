# Project 5: Real-time Data Streaming

Kafka + Flink pipeline for processing portfolio events with exactly-once semantics.

## Run (local simulation)
```bash
pip install -r requirements.txt
python src/process_events.py
```


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Data Pipelines

#### 1. ETL Pipeline
```
Create a Python-based ETL pipeline using Apache Airflow that extracts data from PostgreSQL, transforms it with pandas, and loads it into a data warehouse with incremental updates
```

#### 2. Stream Processing
```
Generate a Kafka consumer in Python that processes real-time events, performs aggregations using sliding windows, and stores results in Redis with TTL
```

#### 3. Data Quality
```
Write a data validation framework that checks for schema compliance, null values, data freshness, and statistical anomalies, with alerting on failures
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

