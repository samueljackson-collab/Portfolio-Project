"""
Lead Time Calculator for Twisted Monk Suite.
Calculates estimated lead times based on historical data and supplier performance.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SupplierTier(Enum):
    """Supplier performance tier classification."""
    PREMIUM = "premium"  # Consistently fast, reliable
    STANDARD = "standard"  # Average performance
    ECONOMY = "economy"  # Longer lead times
    UNTESTED = "untested"  # New supplier, no history


@dataclass
class SupplierProfile:
    """Supplier profile with performance metrics."""
    supplier_id: str
    name: str
    tier: SupplierTier
    average_lead_time_days: int
    on_time_delivery_rate: float  # 0.0 to 1.0
    location: str
    shipping_method: str = "standard"


@dataclass
class LeadTimeEstimate:
    """Lead time estimation result."""
    product_id: str
    supplier_id: str
    estimated_days: int
    earliest_date: datetime
    latest_date: datetime
    confidence: float  # 0.0 to 1.0
    factors: List[str]  # Factors affecting the estimate


class LeadTimeCalculator:
    """
    Calculate product lead times based on multiple factors:
    - Supplier performance history
    - Product complexity
    - Order quantity
    - Seasonal factors
    - Current inventory levels
    """
    
    def __init__(self):
        """Initialize the lead time calculator."""
        self.suppliers: Dict[str, SupplierProfile] = {}
        self._load_default_suppliers()
    
    def _load_default_suppliers(self):
        """Load default supplier profiles."""
        # In production, load from database
        self.suppliers = {
            "SUP001": SupplierProfile(
                supplier_id="SUP001",
                name="Premium Supplier Co.",
                tier=SupplierTier.PREMIUM,
                average_lead_time_days=5,
                on_time_delivery_rate=0.95,
                location="USA",
                shipping_method="express"
            ),
            "SUP002": SupplierProfile(
                supplier_id="SUP002",
                name="Standard Materials Inc.",
                tier=SupplierTier.STANDARD,
                average_lead_time_days=10,
                on_time_delivery_rate=0.85,
                location="Canada",
                shipping_method="standard"
            ),
            "SUP003": SupplierProfile(
                supplier_id="SUP003",
                name="Economy Imports Ltd.",
                tier=SupplierTier.ECONOMY,
                average_lead_time_days=20,
                on_time_delivery_rate=0.75,
                location="China",
                shipping_method="sea freight"
            ),
        }
    
    def add_supplier(self, supplier: SupplierProfile):
        """Add or update a supplier profile."""
        self.suppliers[supplier.supplier_id] = supplier
        logger.info(f"Added/updated supplier: {supplier.supplier_id} - {supplier.name}")
    
    def calculate(
        self,
        supplier_id: str,
        product_id: str,
        quantity: int = 1,
        order_date: Optional[datetime] = None
    ) -> LeadTimeEstimate:
        """
        Calculate lead time estimate for a product order.
        
        Args:
            supplier_id: Supplier identifier
            product_id: Product SKU or ID
            quantity: Order quantity
            order_date: Expected order date (defaults to now)
        
        Returns:
            LeadTimeEstimate with detailed timing information
        
        Raises:
            ValueError: If supplier not found or invalid inputs
        """
        if supplier_id not in self.suppliers:
            raise ValueError(f"Supplier {supplier_id} not found")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        order_date = order_date or datetime.now()
        supplier = self.suppliers[supplier_id]
        
        # Base lead time from supplier profile
        base_days = supplier.average_lead_time_days
        factors = [f"Supplier base: {base_days} days"]
        
        # Adjust for quantity
        quantity_adjustment = 0
        if quantity > 100:
            quantity_adjustment = 3
            factors.append(f"Large order (>100): +{quantity_adjustment} days")
        elif quantity > 50:
            quantity_adjustment = 1
            factors.append(f"Medium order (>50): +{quantity_adjustment} day")
        
        # Adjust for supplier tier
        tier_adjustment = 0
        if supplier.tier == SupplierTier.PREMIUM:
            tier_adjustment = -2
            factors.append(f"Premium supplier: {tier_adjustment} days")
        elif supplier.tier == SupplierTier.ECONOMY:
            tier_adjustment = 3
            factors.append(f"Economy supplier: +{tier_adjustment} days")
        elif supplier.tier == SupplierTier.UNTESTED:
            tier_adjustment = 5
            factors.append(f"Untested supplier: +{tier_adjustment} days (safety buffer)")
        
        # Seasonal adjustment (example: holiday season)
        seasonal_adjustment = self._get_seasonal_adjustment(order_date)
        if seasonal_adjustment != 0:
            factors.append(f"Seasonal factor: {seasonal_adjustment:+d} days")
        
        # Calculate final estimate
        estimated_days = max(1, base_days + quantity_adjustment + tier_adjustment + seasonal_adjustment)
        
        # Calculate confidence based on supplier reliability
        confidence = supplier.on_time_delivery_rate * 0.9  # Cap at 90%
        if supplier.tier == SupplierTier.UNTESTED:
            confidence *= 0.5  # Lower confidence for new suppliers
        
        # Calculate date range (±20% for variability)
        variability_days = max(1, int(estimated_days * 0.2))
        earliest = order_date + timedelta(days=estimated_days - variability_days)
        latest = order_date + timedelta(days=estimated_days + variability_days)
        
        return LeadTimeEstimate(
            product_id=product_id,
            supplier_id=supplier_id,
            estimated_days=estimated_days,
            earliest_date=earliest,
            latest_date=latest,
            confidence=round(confidence, 2),
            factors=factors
        )
    
    def _get_seasonal_adjustment(self, order_date: datetime) -> int:
        """
        Calculate seasonal adjustment for lead time.
        
        Args:
            order_date: Date of order
        
        Returns:
            Adjustment in days (positive or negative)
        """
        month = order_date.month
        
        # Holiday season (November-December): longer lead times
        if month in [11, 12]:
            return 3
        
        # Chinese New Year impact (January-February)
        if month in [1, 2]:
            return 2
        
        # Summer (slower periods): potentially faster
        if month in [7, 8]:
            return -1
        
        return 0
    
    def get_supplier_recommendations(
        self,
        product_id: str,
        required_by_date: datetime,
        quantity: int = 1
    ) -> List[Tuple[SupplierProfile, LeadTimeEstimate]]:
        """
        Get recommended suppliers for a product based on required delivery date.
        
        Args:
            product_id: Product SKU or ID
            required_by_date: Date product is needed
            quantity: Order quantity
        
        Returns:
            List of (supplier, estimate) tuples, sorted by suitability
        """
        recommendations = []
        
        for supplier_id, supplier in self.suppliers.items():
            try:
                estimate = self.calculate(supplier_id, product_id, quantity)
                
                # Check if supplier can meet the deadline
                if estimate.latest_date <= required_by_date:
                    recommendations.append((supplier, estimate))
            except Exception as e:
                logger.warning(f"Error calculating lead time for {supplier_id}: {e}")
        
        # Sort by: 1) confidence, 2) earliest delivery, 3) cost (tier)
        recommendations.sort(
            key=lambda x: (
                -x[1].confidence,  # Higher confidence first
                x[1].earliest_date,  # Earlier delivery first
                x[0].tier.value  # Premium suppliers first
            )
        )
        
        return recommendations
    
    def bulk_calculate(
        self,
        orders: List[Tuple[str, str, int]]
    ) -> Dict[str, LeadTimeEstimate]:
        """
        Calculate lead times for multiple orders.
        
        Args:
            orders: List of (supplier_id, product_id, quantity) tuples
        
        Returns:
            Dictionary mapping product_id to LeadTimeEstimate
        """
        results = {}
        
        for supplier_id, product_id, quantity in orders:
            try:
                estimate = self.calculate(supplier_id, product_id, quantity)
                results[product_id] = estimate
            except Exception as e:
                logger.error(f"Failed to calculate lead time for {product_id}: {e}")
        
        return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    calculator = LeadTimeCalculator()
    
    # Example 1: Single calculation
    estimate = calculator.calculate(
        supplier_id="SUP001",
        product_id="PROD-123",
        quantity=25
    )
    
    print(f"\n=== Lead Time Estimate ===")
    print(f"Product: {estimate.product_id}")
    print(f"Supplier: {estimate.supplier_id}")
    print(f"Estimated Days: {estimate.estimated_days}")
    print(f"Delivery Window: {estimate.earliest_date.date()} to {estimate.latest_date.date()}")
    print(f"Confidence: {estimate.confidence * 100:.0f}%")
    print(f"Factors:")
    for factor in estimate.factors:
        print(f"  - {factor}")
    
    # Example 2: Get recommendations
    from datetime import datetime, timedelta
    required_date = datetime.now() + timedelta(days=15)
    
    print(f"\n=== Supplier Recommendations ===")
    print(f"Required by: {required_date.date()}")
    
    recommendations = calculator.get_supplier_recommendations(
        product_id="PROD-456",
        required_by_date=required_date,
        quantity=50
    )
    
    for i, (supplier, estimate) in enumerate(recommendations, 1):
        print(f"\n{i}. {supplier.name} ({supplier.tier.value})")
        print(f"   Estimated: {estimate.estimated_days} days")
        print(f"   Confidence: {estimate.confidence * 100:.0f}%")
        print(f"   Delivery: {estimate.earliest_date.date()} to {estimate.latest_date.date()}")
