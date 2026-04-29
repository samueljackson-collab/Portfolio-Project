# Troubleshooting Guide

## Backend API

### API returns 503 on `/health`
- Verify Redis connectivity from the API host.
- Confirm Shopify credentials (`SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ACCESS_TOKEN`).
- Check firewall rules allowing outbound HTTPS to Shopify.

### Rate limit errors
- Inspect Redis keys with prefix `rate_limit:` to ensure expiry is working.
- Increase `API_RATE_LIMIT` for trusted integrations.
- Verify clients are reusing API keys instead of generating new ones.

### Inventory updates fail
- Confirm the Shopify location ID and inventory item IDs are correct.
- Ensure the API key used by Shopify has inventory permissions.
- Review API logs for 4xx errors and message details.

## Shopify Theme

### Snippets not rendering
- Confirm snippets were uploaded to the active theme.
- Ensure product template includes `{% render 'availability-badge' %}` and `{% render 'urgency-banner' %}`.
- Check for conflicting CSS classes overriding snippet styles.

### Bundle recommendations not loading
- Inspect browser console for network errors to the API domain.
- Confirm the `data-api-base-url` attribute matches the deployed API endpoint.
- Ensure CORS configuration includes the Shopify storefront domain.

## Operations Scripts

### Lead time report empty
- Confirm supplier APIs respond with valid JSON.
- Ensure vendors map to suppliers in `map_vendor_to_supplier`.
- Verify Shopify API credentials.

### Slack alerts not delivered
- Validate `SLACK_WEBHOOK_URL` in environment variables.
- Review network restrictions blocking outbound webhook calls.
- Check Slack app permissions for the destination channel.

## General Tips

- Enable debug logging by setting `LOG_LEVEL=DEBUG` when testing.
- Use `pytest -k <testname>` to run targeted tests when debugging failures.
- Keep `.env` files synchronized between local, staging, and production environments.
