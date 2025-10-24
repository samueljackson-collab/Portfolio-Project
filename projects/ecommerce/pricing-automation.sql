-- Margin-based price adjustment procedure (anonymized)
CREATE OR REPLACE PROCEDURE apply_margin_adjustments()
LANGUAGE plpgsql
AS $$
DECLARE
    sku_record RECORD;
BEGIN
    FOR sku_record IN
        SELECT sku, cost, target_margin, competitor_price
        FROM pricing_staging
    LOOP
        UPDATE catalog_prices
        SET price = GREATEST(
                ROUND(sku_record.cost * (1 + sku_record.target_margin), 2),
                sku_record.competitor_price - 1.00,
                floor_price
            ),
            last_synced_at = NOW()
        WHERE catalog_prices.sku = sku_record.sku;
    END LOOP;
    INSERT INTO pricing_audit(run_at, updated_count)
    VALUES (NOW(), FOUND);
END;
$$;

-- Execute nightly after catalog ingestion
CALL apply_margin_adjustments();
