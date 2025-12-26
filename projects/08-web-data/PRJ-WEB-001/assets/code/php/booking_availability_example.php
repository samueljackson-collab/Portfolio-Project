<?php
// Sanitized availability checker for bookable items.
// Replace table names with actual prefixes when implementing.

function is_slot_available(PDO $db, int $bookableId, string $startUtc, string $endUtc): bool
{
    $query = <<<SQL
        SELECT COUNT(*) AS conflicts
        FROM WP_BOOKINGS b
        WHERE b.bookable_item_id = :bookable_id
          AND b.status IN ('confirmed', 'hold')
          AND NOT (
              b.end_utc <= :start_utc
              OR b.start_utc >= :end_utc
          )
    SQL;

    $stmt = $db->prepare($query);
    $stmt->execute([
        ':bookable_id' => $bookableId,
        ':start_utc' => $startUtc,
        ':end_utc'   => $endUtc,
    ]);

    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return ((int) $row['conflicts']) === 0;
}

function hold_slot(PDO $db, int $bookableId, string $startUtc, string $endUtc, string $customerEmail): bool
{
    if (!is_slot_available($db, $bookableId, $startUtc, $endUtc)) {
        return false;
    }

    $stmt = $db->prepare(
        'INSERT INTO WP_BOOKINGS (bookable_item_id, start_utc, end_utc, status, customer_email, hold_expires_utc)
         VALUES (:id, :start, :end, "hold", :email, DATE_ADD(:start, INTERVAL 30 MINUTE))'
    );

    return $stmt->execute([
        ':id'    => $bookableId,
        ':start' => $startUtc,
        ':end'   => $endUtc,
        ':email' => filter_var($customerEmail, FILTER_SANITIZE_EMAIL),
    ]);
}

// Usage example (staging only):
// $pdo = new PDO('mysql:host=localhost;dbname=sanitized', 'user', 'pass', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
// $isAvailable = hold_slot($pdo, 42, '2025-12-20 15:00:00', '2025-12-22 11:00:00', 'guest@example.com');
// var_dump($isAvailable);
?>
