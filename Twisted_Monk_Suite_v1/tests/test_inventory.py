import pytest
from pydantic import ValidationError

from Twisted_Monk_Suite_v1.backend.main import BundleRecommendationRequest, generate_recommendations


def test_generate_recommendations_prefers_matching_tags():
    current_product = {
        "id": 1,
        "title": "Primary",
        "product_type": "Gear",
        "tags": "rope, silk",
        "variants": [{"price": "20.00", "inventory_quantity": 3}],
    }
    other_products = [
        {
            "id": 2,
            "title": "Matching",
            "product_type": "Gear",
            "tags": "rope, steel",
            "handle": "matching",
            "variants": [{"price": "19.00", "inventory_quantity": 5}],
            "images": [{"src": "https://example.com/a.jpg"}],
        },
        {
            "id": 3,
            "title": "Unrelated",
            "product_type": "Other",
            "tags": "different",
            "handle": "unrelated",
            "variants": [{"price": "40.00", "inventory_quantity": 10}],
            "images": [{"src": "https://example.com/b.jpg"}],
        },
    ]

    recommendations = generate_recommendations(current_product, other_products, limit=2)
    assert len(recommendations) == 1
    assert recommendations[0].product_id == "2"
    assert recommendations[0].reason in {"Frequently purchased together", "Similar style and features", "Complements your Gear"}


def test_bundle_request_validation():
    request = BundleRecommendationRequest(product_id="1", limit=4)
    assert request.limit == 4
    with pytest.raises(ValidationError):
        BundleRecommendationRequest(product_id="1", limit=0)
