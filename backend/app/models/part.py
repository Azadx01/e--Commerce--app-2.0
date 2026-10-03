from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    part_type = Column(String(50), index=True, nullable=False)  # Screen, Battery, Charging Port, Camera, etc.
    manufacturer = Column(String(100), index=True, nullable=False)
    condition = Column(String(50), index=True, nullable=False)  # OEM, COMPATIBLE_THIRD_PARTY, USED_TESTED
    price = Column(Float, nullable=False)
    warranty = Column(String(100), nullable=False)  # e.g. "180 days warranty"
    stock = Column(Integer, default=0, nullable=False)
    seller = Column(String(100), index=True, nullable=False)
    
    # Structured compatibility rules: list of target categories, brands, and models
    # Example: [{"category": "smartphone", "brand": "Samsung", "models": ["Galaxy S23", "SM-S911B"]}]
    compatibility = Column(JSON, nullable=False, default=list)
    
    description = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    rating = Column(Float, default=4.8, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def is_compatible_with(self, category: str = None, brand: str = None, model: str = None) -> bool:
        """
        Device-model compatibility engine rule evaluation.
        A part is ONLY recommended if compatibility rules allow it.
        """
        if not self.compatibility:
            return False

        rules = self.compatibility if isinstance(self.compatibility, list) else [self.compatibility]
        
        for rule in rules:
            rule_cat = rule.get("category", "").lower() if rule.get("category") else None
            rule_brand = rule.get("brand", "").lower() if rule.get("brand") else None
            rule_models = [m.lower() for m in rule.get("models", [])] if rule.get("models") else []

            # 1. Category check (if requested)
            if category and rule_cat and category.lower() != rule_cat:
                continue

            # 2. Brand check (if requested)
            if brand and rule_brand and brand.lower() != rule_brand:
                continue

            # 3. Model check (if requested)
            if model:
                target_model = model.strip().lower()
                # Check if exact model in list or substring / pattern match in models
                matched_model = False
                for rm in rule_models:
                    if rm in target_model or target_model in rm:
                        matched_model = True
                        break
                if not matched_model and rule_models:
                    continue

            return True

        return False
