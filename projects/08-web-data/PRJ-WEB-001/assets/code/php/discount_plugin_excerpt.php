<?php
/**
 * WooCommerce Discount Logic Plugin — Sanitized Excerpt
 *
 * Original implementation: Custom wholesale/retail discount engine for a
 * 10,000+ SKU flooring store. Handles tiered pricing, customer group discounts,
 * and promotional code stacking with conflict resolution.
 *
 * Evidence type: Sanitized code sample (client names, product IDs, and
 * pricing data have been replaced with generic placeholders).
 *
 * Original environment: WordPress 6.x, WooCommerce 8.x, PHP 8.1
 */

// Prevent direct file access
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Class: Custom_Discount_Engine
 *
 * Applies tiered pricing and wholesale discounts to cart items.
 * Hooks into WooCommerce price calculation filters to modify unit
 * prices based on customer role, order quantity, and active promotions.
 */
class Custom_Discount_Engine {

    /**
     * Discount tiers keyed by customer role.
     * Format: [ role => [ min_qty => discount_pct ] ]
     */
    private array $tier_matrix = [
        'wholesale_customer' => [
            1   => 0.15,   // 15% off 1+ units
            50  => 0.20,   // 20% off 50+ units
            200 => 0.25,   // 25% off 200+ units
        ],
        'trade_customer' => [
            1   => 0.10,   // 10% off 1+ units
            25  => 0.15,   // 15% off 25+ units
        ],
        'retail_customer' => [
            1   => 0.00,   // No base discount
            10  => 0.05,   // 5% off 10+ units (bulk retail)
        ],
    ];

    /**
     * Maximum stackable promotional discount on top of role-based discount.
     */
    private const MAX_PROMO_STACK = 0.10; // 10%

    public function __construct() {
        add_filter( 'woocommerce_product_get_price', [ $this, 'apply_role_discount' ], 10, 2 );
        add_filter( 'woocommerce_cart_item_price',   [ $this, 'display_discounted_price' ], 10, 3 );
        add_action( 'woocommerce_before_calculate_totals', [ $this, 'apply_cart_level_discounts' ], 20 );
    }

    /**
     * Returns the discount percentage for a given customer role and item quantity.
     *
     * @param string $role     WooCommerce customer role slug.
     * @param int    $quantity Number of units in cart line item.
     * @return float           Discount as a decimal (e.g. 0.20 = 20%).
     */
    public function get_tier_discount( string $role, int $quantity ): float {
        if ( ! isset( $this->tier_matrix[ $role ] ) ) {
            return 0.0;
        }

        $applicable_discount = 0.0;

        foreach ( $this->tier_matrix[ $role ] as $min_qty => $discount ) {
            if ( $quantity >= $min_qty ) {
                $applicable_discount = $discount;
            }
        }

        return $applicable_discount;
    }

    /**
     * Applies role-based discount to individual product price.
     * Hooked to: woocommerce_product_get_price
     *
     * @param string      $price   Original product price (string from WC).
     * @param \WC_Product $product Product object.
     * @return string              Modified price as string.
     */
    public function apply_role_discount( string $price, \WC_Product $product ): string {
        // Skip admin context to avoid affecting cost display in backend
        if ( is_admin() && ! defined( 'DOING_AJAX' ) ) {
            return $price;
        }

        $user        = wp_get_current_user();
        $role        = $this->get_primary_role( $user );
        $cart        = WC()->cart;
        $quantity    = $cart ? $this->get_product_quantity_in_cart( $product->get_id() ) : 1;
        $discount    = $this->get_tier_discount( $role, $quantity );

        if ( $discount <= 0 ) {
            return $price;
        }

        $discounted = (float) $price * ( 1 - $discount );

        // Round to 2 decimal places to avoid floating point artifacts
        return (string) round( $discounted, 2 );
    }

    /**
     * Applies cart-level promotional stacking after role discounts are set.
     * Hooked to: woocommerce_before_calculate_totals (priority 20, after role discounts)
     *
     * @param \WC_Cart $cart Active cart object.
     * @return void
     */
    public function apply_cart_level_discounts( \WC_Cart $cart ): void {
        if ( is_admin() && ! defined( 'DOING_AJAX' ) ) {
            return;
        }

        $promo_code   = WC()->session->get( 'active_promo_code', '' );
        $promo_pct    = $this->resolve_promo_discount( $promo_code );

        if ( $promo_pct <= 0 ) {
            return;
        }

        // Cap stacked promotional discount to prevent abuse
        $effective_promo = min( $promo_pct, self::MAX_PROMO_STACK );

        foreach ( $cart->get_cart() as $cart_item_key => $cart_item ) {
            $product  = $cart_item['data'];
            $current  = (float) $product->get_price();
            $adjusted = $current * ( 1 - $effective_promo );

            $product->set_price( round( $adjusted, 2 ) );
        }
    }

    /**
     * Resolves promotional code to a discount percentage.
     * In production, this queried a custom DB table of active promo records.
     *
     * @param string $code Promotional code entered at checkout.
     * @return float       Discount as decimal (e.g. 0.08 = 8%).
     */
    private function resolve_promo_discount( string $code ): float {
        // Sanitized: Original implementation queried wp_custom_promos table
        // Schema: (code VARCHAR, discount_pct DECIMAL, expiry DATE, max_uses INT, uses INT)
        global $wpdb;

        $result = $wpdb->get_var(
            $wpdb->prepare(
                "SELECT discount_pct
                   FROM {$wpdb->prefix}custom_promos
                  WHERE code = %s
                    AND expiry >= CURDATE()
                    AND (max_uses = 0 OR uses < max_uses)
                  LIMIT 1",
                sanitize_text_field( $code )
            )
        );

        return $result ? (float) $result : 0.0;
    }

    /**
     * Returns the primary WP role for a user (first non-subscriber role).
     *
     * @param \WP_User $user WordPress user object.
     * @return string        Role slug, defaults to 'retail_customer'.
     */
    private function get_primary_role( \WP_User $user ): string {
        $priority_roles = [ 'wholesale_customer', 'trade_customer', 'retail_customer' ];

        foreach ( $priority_roles as $role ) {
            if ( in_array( $role, (array) $user->roles, true ) ) {
                return $role;
            }
        }

        return 'retail_customer';
    }

    /**
     * Returns total quantity of a product currently in the cart (all variations).
     *
     * @param int $product_id WooCommerce product ID.
     * @return int            Total quantity across all cart line items for this product.
     */
    private function get_product_quantity_in_cart( int $product_id ): int {
        $cart  = WC()->cart;
        $total = 0;

        if ( ! $cart ) {
            return 1;
        }

        foreach ( $cart->get_cart() as $item ) {
            $item_product_id = $item['product_id'] ?? 0;
            if ( (int) $item_product_id === $product_id ) {
                $total += (int) ( $item['quantity'] ?? 1 );
            }
        }

        return max( 1, $total );
    }

    /**
     * Formats and displays the discounted price in the cart table.
     * Hooked to: woocommerce_cart_item_price
     *
     * @param string $price_html   Original price HTML from WooCommerce.
     * @param array  $cart_item    Cart item array.
     * @param string $cart_item_key Unique cart item key.
     * @return string              Modified price HTML with original price struck through.
     */
    public function display_discounted_price( string $price_html, array $cart_item, string $cart_item_key ): string {
        $product      = $cart_item['data'];
        $regular      = (float) $product->get_regular_price();
        $current      = (float) $product->get_price();

        // Only modify display if a discount has been applied
        if ( $current >= $regular || $regular <= 0 ) {
            return $price_html;
        }

        $savings_pct = round( ( 1 - $current / $regular ) * 100 );

        $original_html  = '<del>' . wc_price( $regular ) . '</del>';
        $sale_html      = '<ins>' . wc_price( $current ) . '</ins>';
        $badge_html     = '<span class="discount-badge">-' . $savings_pct . '%</span>';

        return $original_html . ' ' . $sale_html . ' ' . $badge_html;
    }
}

// Initialize plugin on WooCommerce loaded hook
add_action( 'woocommerce_loaded', function () {
    new Custom_Discount_Engine();
} );
