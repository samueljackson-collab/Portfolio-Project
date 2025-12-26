<?php
// Sanitized booking rate calculator (excerpt)
// Inputs: nightly base rate, occupancy, seasonal multiplier, optional promo code
// Output: normalized rate array used by checkout flow

function calculate_booking_rate(array $params): array {
    $base = (float) ($params['base_rate'] ?? 0);
    $occupancy = max(1, (int) ($params['occupancy'] ?? 1));
    $seasonal = (float) ($params['seasonal_multiplier'] ?? 1.0);
    $promo = sanitize_text_field($params['promo_code'] ?? '');

    // Apply seasonal pricing
    $rate = $base * $seasonal;

    // Adjust for occupancy (additional guests beyond 2 add 10%)
    if ($occupancy > 2) {
        $rate += ($occupancy - 2) * ($base * 0.10);
    }

    // Apply promo code discount (sanitized lookup)
    if ($promo && promo_is_valid($promo)) {
        $rate = apply_promo_discount($rate, $promo);
    }

    // Floor to two decimals and return structured response
    return [
        'nightly_rate' => round($rate, 2),
        'currency' => 'USD',
        'rules' => [
            'seasonal_multiplier' => $seasonal,
            'occupancy' => $occupancy,
            'promo_applied' => (bool) $promo,
        ],
    ];
}

function promo_is_valid(string $code): bool {
    // Placeholder validation; real implementation checks expiry + usage limit
    $allowed = ['WELCOME10', 'FALL15'];
    return in_array(strtoupper($code), $allowed, true);
}

function apply_promo_discount(float $amount, string $code): float {
    $discounts = [
        'WELCOME10' => 0.10,
        'FALL15' => 0.15,
    ];
    $pct = $discounts[strtoupper($code)] ?? 0;
    return $amount * (1 - $pct);
}
