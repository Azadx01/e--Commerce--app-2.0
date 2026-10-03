from sqlalchemy.orm import Session
from app.models.part import Part

DEFAULT_PARTS = [
    # --- Samsung Galaxy S23 Parts ---
    {
        "sku": "SKU-SAM-S23-DISP-OEM",
        "name": "Samsung Galaxy S23 Dynamic AMOLED 2X Display (OEM)",
        "part_type": "Screen",
        "manufacturer": "Samsung Electronics",
        "condition": "OEM",
        "price": 145.0,
        "warranty": "180 days manufacturer warranty",
        "stock": 15,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Samsung",
                "models": ["Galaxy S23", "Galaxy S23 5G", "SM-S911B", "SM-S911U"],
                "notes": "Direct OEM fit with factory color calibration."
            }
        ],
        "description": "Original Samsung 6.1-inch 120Hz Dynamic AMOLED 2X display assembly with frame and digitizer.",
        "image_url": "https://revivo-cdn.internal/parts/sam-s23-screen-oem.jpg",
        "rating": 4.9,
    },
    {
        "sku": "SKU-SAM-S23-BAT-OEM",
        "name": "Samsung Galaxy S23 3900mAh Li-ion Battery (OEM)",
        "part_type": "Battery",
        "manufacturer": "Samsung Electronics",
        "condition": "OEM",
        "price": 48.0,
        "warranty": "1 year warranty",
        "stock": 28,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Samsung",
                "models": ["Galaxy S23", "SM-S911B"],
                "notes": "Original 3.88V 3900mAh cell with NFC antenna integration."
            }
        ],
        "description": "Genuine OEM replacement battery for Samsung Galaxy S23 base model.",
        "image_url": "https://revivo-cdn.internal/parts/sam-s23-battery-oem.jpg",
        "rating": 4.8,
    },
    {
        "sku": "SKU-SAM-S23-DISP-TP",
        "name": "Galaxy S23 Hard OLED Display Assembly (Compatible Third-Party)",
        "part_type": "Screen",
        "manufacturer": "JK Displays",
        "condition": "COMPATIBLE_THIRD_PARTY",
        "price": 85.0,
        "warranty": "90 days warranty",
        "stock": 22,
        "seller": "Apex Mobile Spares",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Samsung",
                "models": ["Galaxy S23", "SM-S911B"],
                "notes": "High quality aftermarket OLED panel with full touch response."
            }
        ],
        "description": "Cost-effective third-party replacement OLED screen assembly.",
        "image_url": "https://revivo-cdn.internal/parts/sam-s23-screen-tp.jpg",
        "rating": 4.5,
    },
    {
        "sku": "SKU-SAM-S23-CAM-USED",
        "name": "Samsung Galaxy S23 50MP Main Camera Module (Used Tested Grade A)",
        "part_type": "Camera",
        "manufacturer": "Samsung Original Pull",
        "condition": "USED_TESTED",
        "price": 55.0,
        "warranty": "60 days tested warranty",
        "stock": 7,
        "seller": "EcoParts Refurb",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Samsung",
                "models": ["Galaxy S23", "Galaxy S23+"],
                "notes": "100% verified OIS focus and sensor clarity tested on optical rig."
            }
        ],
        "description": "Tested working OEM camera pulled from undamaged donor board.",
        "image_url": "https://revivo-cdn.internal/parts/sam-s23-camera-used.jpg",
        "rating": 4.7,
    },

    # --- Google Pixel 7 Pro Parts ---
    {
        "sku": "SKU-GOOG-P7P-DISP-OEM",
        "name": "Google Pixel 7 Pro 120Hz LTPO OLED Screen (OEM)",
        "part_type": "Screen",
        "manufacturer": "Google Original",
        "condition": "OEM",
        "price": 160.0,
        "warranty": "180 days manufacturer warranty",
        "stock": 10,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Google",
                "models": ["Pixel 7 Pro", "GE2AE", "GP4BC"],
                "notes": "Original 6.7-inch QHD+ 120Hz LTPO display."
            }
        ],
        "description": "Factory genuine Google Pixel 7 Pro OLED screen with optical fingerprint sensor alignment.",
        "image_url": "https://revivo-cdn.internal/parts/goog-p7p-screen-oem.jpg",
        "rating": 4.9,
    },
    {
        "sku": "SKU-GOOG-P7P-BAT-USED",
        "name": "Google Pixel 7 Pro 5000mAh Battery (Used Tested 96% Health)",
        "part_type": "Battery",
        "manufacturer": "Google Original Pull",
        "condition": "USED_TESTED",
        "price": 32.0,
        "warranty": "90 days warranty",
        "stock": 12,
        "seller": "EcoParts Refurb",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Google",
                "models": ["Pixel 7 Pro"],
                "notes": "Cycle count < 100 with battery health verified at 96%."
            }
        ],
        "description": "Certified tested OEM battery pulled from recycled low-cycle unit.",
        "image_url": "https://revivo-cdn.internal/parts/goog-p7p-battery-used.jpg",
        "rating": 4.6,
    },
    {
        "sku": "SKU-GOOG-P7P-PORT-TP",
        "name": "Google Pixel 7 Pro USB-C Charging Port Board (Compatible Third-Party)",
        "part_type": "Charging Port",
        "manufacturer": "AmpTech Supply",
        "condition": "COMPATIBLE_THIRD_PARTY",
        "price": 18.5,
        "warranty": "180 days warranty",
        "stock": 35,
        "seller": "Global Tech Spares",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Google",
                "models": ["Pixel 7 Pro"],
                "notes": "Supports Power Delivery 3.0 fast charging and microphone input."
            }
        ],
        "description": "Precision aftermarket replacement daughterboard with microphone and USB-C socket.",
        "image_url": "https://revivo-cdn.internal/parts/goog-p7p-port-tp.jpg",
        "rating": 4.7,
    },

    # --- Apple iPhone 14 Pro Parts ---
    {
        "sku": "SKU-APP-IP14P-DISP-OEM",
        "name": "Apple iPhone 14 Pro Super Retina XDR OLED (OEM Original)",
        "part_type": "Screen",
        "manufacturer": "Apple Original",
        "condition": "OEM",
        "price": 260.0,
        "warranty": "1 year warranty",
        "stock": 8,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Apple",
                "models": ["iPhone 14 Pro", "A2890", "A2650"],
                "notes": "Dynamic Island compatible ProMotion 120Hz display."
            }
        ],
        "description": "Original genuine Apple iPhone 14 Pro OLED screen assembly with True Tone support.",
        "image_url": "https://revivo-cdn.internal/parts/app-ip14p-screen-oem.jpg",
        "rating": 5.0,
    },
    {
        "sku": "SKU-APP-IP14P-BAT-TP",
        "name": "iPhone 14 Pro High-Capacity Battery (Compatible Third-Party)",
        "part_type": "Battery",
        "manufacturer": "iFixit / Amprius",
        "condition": "COMPATIBLE_THIRD_PARTY",
        "price": 42.0,
        "warranty": "180 days warranty",
        "stock": 18,
        "seller": "Apex Mobile Spares",
        "compatibility": [
            {
                "category": "smartphone",
                "brand": "Apple",
                "models": ["iPhone 14 Pro"],
                "notes": "TI battery management IC with zero cycle count."
            }
        ],
        "description": "Direct replacement battery pack with pre-applied adhesive strips.",
        "image_url": "https://revivo-cdn.internal/parts/app-ip14p-battery-tp.jpg",
        "rating": 4.6,
    },

    # --- Dell Laptop Parts ---
    {
        "sku": "SKU-DELL-XPS13-BAT-OEM",
        "name": "Dell XPS 13 9310 52Wh 4-Cell OEM Battery",
        "part_type": "Battery",
        "manufacturer": "Dell Inc",
        "condition": "OEM",
        "price": 85.0,
        "warranty": "1 year manufacturer warranty",
        "stock": 14,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "laptop",
                "brand": "Dell",
                "models": ["XPS 13 9310", "XPS 13 9305", "XPS 13 9300"],
                "notes": "Original 7.6V 52Wh Type 70N2F battery."
            }
        ],
        "description": "Brand new original Dell laptop battery for XPS 13 ultrabooks.",
        "image_url": "https://revivo-cdn.internal/parts/dell-xps13-bat-oem.jpg",
        "rating": 4.9,
    },
    {
        "sku": "SKU-DELL-XPS13-KB-USED",
        "name": "Dell XPS 13 Backlit US Keyboard Assembly (Used Tested)",
        "part_type": "Keyboard",
        "manufacturer": "Dell Original Pull",
        "condition": "USED_TESTED",
        "price": 40.0,
        "warranty": "90 days warranty",
        "stock": 5,
        "seller": "EcoParts Refurb",
        "compatibility": [
            {
                "category": "laptop",
                "brand": "Dell",
                "models": ["XPS 13 9310", "XPS 13 9300"],
                "notes": "Tested key switch travel and LED backlight uniformity."
            }
        ],
        "description": "Original US English backlit keyboard module pulled from tested laptop.",
        "image_url": "https://revivo-cdn.internal/parts/dell-xps13-kb-used.jpg",
        "rating": 4.5,
    },

    # --- Apple MacBook Pro Parts ---
    {
        "sku": "SKU-APP-MBP14-DISP-OEM",
        "name": "MacBook Pro 14 Liquid Retina XDR Complete Display (OEM)",
        "part_type": "Screen",
        "manufacturer": "Apple Original",
        "condition": "OEM",
        "price": 450.0,
        "warranty": "180 days warranty",
        "stock": 4,
        "seller": "ReVivo Official Store",
        "compatibility": [
            {
                "category": "laptop",
                "brand": "Apple",
                "models": ["MacBook Pro 14", "A2442", "A2779"],
                "notes": "Complete top clamshell assembly with camera and ambient light sensor."
            }
        ],
        "description": "Original Space Gray 14-inch mini-LED Liquid Retina XDR display lid assembly.",
        "image_url": "https://revivo-cdn.internal/parts/app-mbp14-disp-oem.jpg",
        "rating": 5.0,
    }
]

def seed_parts(db: Session) -> int:
    """Seeds default spare parts if parts table is currently empty."""
    count = db.query(Part).count()
    if count > 0:
        return count

    for item in DEFAULT_PARTS:
        part = Part(
            sku=item["sku"],
            name=item["name"],
            part_type=item["part_type"],
            manufacturer=item["manufacturer"],
            condition=item["condition"],
            price=item["price"],
            warranty=item["warranty"],
            stock=item["stock"],
            seller=item["seller"],
            compatibility=item["compatibility"],
            description=item.get("description"),
            image_url=item.get("image_url"),
            rating=item.get("rating", 4.8),
            is_active=True,
        )
        db.add(part)
    
    db.commit()
    return len(DEFAULT_PARTS)
