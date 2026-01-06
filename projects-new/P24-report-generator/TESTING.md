# Testing

Automated commands:
- `make lint`
- `pytest tests`
- `python scripts/render_sample.py --template invoices`

Manual validation:
- Verify generated report contains all expected template sections
- Check PDF output renders correctly with proper formatting
- Validate digital signature is applied and verifiable
- Confirm Celery worker processes tasks from queue successfully
- Test report delivery mechanism (email/S3 upload) works end-to-end
