from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.db.database import get_db
from app.db.seed_parts import seed_parts
from app.models.part import Part
from app.models.user import User
from app.schemas.part import (
    PartResponse,
    PartListResponse,
    PartCreate,
    PartUpdate,
    PartCondition,
)
from app.api import deps

router = APIRouter()

@router.get("", response_model=PartListResponse)
def list_spare_parts(
    *,
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search term matching name, SKU, manufacturer, or description"),
    condition: Optional[str] = Query(None, description="Filter by condition: OEM, COMPATIBLE_THIRD_PARTY, USED_TESTED"),
    device_category: Optional[str] = Query(None, description="Filter by device category: smartphone or laptop"),
    device_brand: Optional[str] = Query(None, description="Filter by device brand: e.g. Apple, Samsung, Google, Dell"),
    device_model: Optional[str] = Query(None, description="Filter by device model: e.g. Galaxy S23, Pixel 7 Pro"),
    part_type: Optional[str] = Query(None, description="Filter by component type: Screen, Battery, Camera, etc."),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    in_stock_only: Optional[bool] = Query(False, description="Filter to only in-stock parts"),
    seller: Optional[str] = Query(None, description="Filter by seller / distributor"),
    sort_by: Optional[str] = Query(None, description="Sort options: price_asc, price_desc, rating, newest, stock"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Search and filter spare parts catalog with strict device-model compatibility rules.
    IMPORTANT: Parts are only returned/recommended if compatibility rules allow it for the requested device.
    """
    # Ensure baseline catalog is seeded
    seed_parts(db)

    db_query = db.query(Part).filter(Part.is_active == True)

    # 1. Condition filter
    if condition:
        cond_clean = condition.strip().upper()
        allowed_conditions = {c.value for c in PartCondition}
        if cond_clean in allowed_conditions:
            db_query = db_query.filter(Part.condition == cond_clean)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid condition '{condition}'. Must be one of: {', '.join(allowed_conditions)}"
            )

    # 2. Part Type filter
    if part_type:
        db_query = db_query.filter(Part.part_type.ilike(f"%{part_type.strip()}%"))

    # 3. Text search
    if query:
        search_pattern = f"%{query.strip()}%"
        db_query = db_query.filter(
            or_(
                Part.name.ilike(search_pattern),
                Part.sku.ilike(search_pattern),
                Part.manufacturer.ilike(search_pattern),
                Part.description.ilike(search_pattern),
                Part.seller.ilike(search_pattern),
            )
        )

    # 4. Price filters
    if min_price is not None:
        db_query = db_query.filter(Part.price >= min_price)
    if max_price is not None:
        db_query = db_query.filter(Part.price <= max_price)

    # 5. Stock filter
    if in_stock_only:
        db_query = db_query.filter(Part.stock > 0)

    # 6. Seller filter
    if seller:
        db_query = db_query.filter(Part.seller.ilike(f"%{seller.strip()}%"))

    # 7. Sorting
    if sort_by == "price_asc":
        db_query = db_query.order_by(asc(Part.price))
    elif sort_by == "price_desc":
        db_query = db_query.order_by(desc(Part.price))
    elif sort_by == "rating":
        db_query = db_query.order_by(desc(Part.rating))
    elif sort_by == "stock":
        db_query = db_query.order_by(desc(Part.stock))
    else:
        db_query = db_query.order_by(desc(Part.created_at))

    candidates = db_query.all()

    # 8. Device-Model Compatibility Engine Filter
    # IMPORTANT: Do not recommend a part unless compatibility rules allow it!
    has_compat_filter = bool(device_category or device_brand or device_model)
    if has_compat_filter:
        compatible_parts = [
            p for p in candidates
            if p.is_compatible_with(category=device_category, brand=device_brand, model=device_model)
        ]
    else:
        compatible_parts = candidates

    total_count = len(compatible_parts)
    paginated_items = compatible_parts[skip : skip + limit]

    return PartListResponse(
        items=paginated_items,
        total=total_count,
        skip=skip,
        limit=limit,
    )

@router.get("/{id}", response_model=PartResponse)
def get_part_by_id(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Get detailed spare part information by ID including compatibility matrix, seller, and warranty.
    """
    seed_parts(db)
    part = db.query(Part).filter(Part.id == id, Part.is_active == True).first()
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part with ID {id} not found"
        )
    return part

@router.post("", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def create_spare_part(
    *,
    db: Session = Depends(get_db),
    part_in: PartCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a new spare part to the catalog. Admin or verified technician/supplier only.
    """
    if current_user.role not in ["admin", "technician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and suppliers can create spare parts in catalog"
        )

    existing = db.query(Part).filter(Part.sku == part_in.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Part with SKU '{part_in.sku}' already exists"
        )

    # Convert compatibility rules to JSON serializable list
    compat_data = [c.model_dump() for c in part_in.compatibility]

    part = Part(
        sku=part_in.sku,
        name=part_in.name,
        part_type=part_in.part_type,
        manufacturer=part_in.manufacturer,
        condition=part_in.condition.value,
        price=part_in.price,
        warranty=part_in.warranty,
        stock=part_in.stock,
        seller=part_in.seller,
        compatibility=compat_data,
        description=part_in.description,
        image_url=part_in.image_url,
        rating=part_in.rating or 4.8,
        is_active=part_in.is_active if part_in.is_active is not None else True,
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part
