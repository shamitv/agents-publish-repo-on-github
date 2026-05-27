"""Product attribute set data models for catalog service."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductAttributeSet:
    """Attribute definition per category."""
    attr_id: int = 0
    category: str = ""
    attr_name: str = ""
    data_type: str = "string"  # string, number, boolean, date
    required: bool = False


@dataclass
class ProductAttributeValue:
    """Attribute value per product."""
    product_id: int = 0
    attr_id: int = 0
    value: str = ""


# Seed attribute definitions (3-5 per category)
ATTRIBUTE_DEFINITIONS: list[ProductAttributeSet] = [
    # Hardware attributes
    ProductAttributeSet(attr_id=1, category="Hardware", attr_name="Processor Speed", data_type="string", required=True),
    ProductAttributeSet(attr_id=2, category="Hardware", attr_name="Memory Size", data_type="string", required=True),
    ProductAttributeSet(attr_id=3, category="Hardware", attr_name="Connectivity", data_type="string", required=False),
    ProductAttributeSet(attr_id=4, category="Hardware", attr_name="Power Rating", data_type="number", required=True),
    # Wearables attributes
    ProductAttributeSet(attr_id=5, category="Wearables", attr_name="Size", data_type="string", required=True),
    ProductAttributeSet(attr_id=6, category="Wearables", attr_name="Material", data_type="string", required=True),
    ProductAttributeSet(attr_id=7, category="Wearables", attr_name="Battery Life", data_type="string", required=False),
    ProductAttributeSet(attr_id=8, category="Wearables", attr_name="Water Resistant", data_type="boolean", required=False),
    # Cyberware attributes
    ProductAttributeSet(attr_id=9, category="Cyberware", attr_name="Installation Type", data_type="string", required=True),
    ProductAttributeSet(attr_id=10, category="Cyberware", attr_name="Rejection Risk", data_type="string", required=True),
    ProductAttributeSet(attr_id=11, category="Cyberware", attr_name="Recovery Time", data_type="string", required=True),
    # Tactical attributes
    ProductAttributeSet(attr_id=12, category="Tactical", attr_name="Classification", data_type="string", required=True),
    ProductAttributeSet(attr_id=13, category="Tactical", attr_name="Range", data_type="string", required=True),
    ProductAttributeSet(attr_id=14, category="Tactical", attr_name="Weight", data_type="number", required=True),
    ProductAttributeSet(attr_id=15, category="Tactical", attr_name="Safety Rating", data_type="string", required=False),
    # Apparel attributes
    ProductAttributeSet(attr_id=16, category="Apparel", attr_name="Size Range", data_type="string", required=True),
    ProductAttributeSet(attr_id=17, category="Apparel", attr_name="Material Blend", data_type="string", required=True),
    ProductAttributeSet(attr_id=18, category="Apparel", attr_name="Care Instructions", data_type="string", required=False),
]


ATTRIBUTE_VALUES: list[ProductAttributeValue] = [
    # Neural Uplink Core v4 (Hardware)
    ProductAttributeValue(product_id=1, attr_id=1, value="2.4 GHz Quantum Core"),
    ProductAttributeValue(product_id=1, attr_id=2, value="128 TB Neural Storage"),
    ProductAttributeValue(product_id=1, attr_id=3, value="WiFi 7, Bluetooth 6.0, Neural Link"),
    ProductAttributeValue(product_id=1, attr_id=4, value="45W"),
    # Holographic Cyber-Visor (Wearables)
    ProductAttributeValue(product_id=2, attr_id=5, value="M/L/XL"),
    ProductAttributeValue(product_id=2, attr_id=6, value="Polycarbonate, Titanium Frame"),
    ProductAttributeValue(product_id=2, attr_id=7, value="24 hours continuous"),
    ProductAttributeValue(product_id=2, attr_id=8, value="true"),
    # Subdermal Armor Plating (Cyberware)
    ProductAttributeValue(product_id=3, attr_id=9, value="Surgical Implant"),
    ProductAttributeValue(product_id=3, attr_id=10, value="Low (2%)"),
    ProductAttributeValue(product_id=3, attr_id=11, value="3-5 days"),
    # Monofilament Laser-Whip (Tactical)
    ProductAttributeValue(product_id=4, attr_id=12, value="Restricted"),
    ProductAttributeValue(product_id=4, attr_id=13, value="3 meters"),
    ProductAttributeValue(product_id=4, attr_id=14, value="0.8 kg"),
    ProductAttributeValue(product_id=4, attr_id=15, value="Class 4"),
    # Neon Mesh Trenchcoat (Apparel)
    ProductAttributeValue(product_id=5, attr_id=16, value="S-3XL"),
    ProductAttributeValue(product_id=5, attr_id=17, value="85% Nylon, 15% Conductive Fiber"),
    ProductAttributeValue(product_id=5, attr_id=18, value="Hand wash only, do not bleach"),
]


def get_attributes_by_category(category: str) -> list[ProductAttributeSet]:
    return [a for a in ATTRIBUTE_DEFINITIONS if a.category == category]


def get_attribute_values(product_id: int) -> list[ProductAttributeValue]:
    return [v for v in ATTRIBUTE_VALUES if v.product_id == product_id]
