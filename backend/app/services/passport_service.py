import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.repair import Repair
from app.models.quote import Quote
from app.models.technician import TechnicianProfile
from app.models.diagnostic import Diagnostic
from app.schemas.device import (
    DevicePassportResponse,
    PassportWarranty,
    PassportRepairItem,
    PassportResaleValuation,
    PassportLifecycleEvent,
)

def ensure_utc(dt: Optional[datetime]) -> datetime:
    """Ensure datetime is timezone-aware in UTC to prevent offset-naive comparisons."""
    if not dt:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_warranty_days(warranty_str: Optional[str]) -> int:
    """Helper to parse warranty days from string like '90 days', '180 days', '1 year'."""
    if not warranty_str:
        return 90
    clean = warranty_str.lower()
    if "1 year" in clean or "12 month" in clean:
        return 365
    if "2 year" in clean or "24 month" in clean:
        return 730
    if "6 month" in clean or "180 day" in clean:
        return 180
    if "3 month" in clean or "90 day" in clean:
        return 90
    if "30 day" in clean or "1 month" in clean:
        return 30
    match = re.search(r"(\d+)\s*day", clean)
    if match:
        return int(match.group(1))
    return 90

def build_device_passport(db: Session, device: Device) -> DevicePassportResponse:
    now = datetime.now(timezone.utc)
    
    # 1. Masked Identifier (Privacy Protection - never expose raw serial number / IMEI)
    masked_sn = f"DEV-{device.brand[:3].upper()}-{device.id:04d}-SECURE"

    # 2. Gather All Repairs
    repairs = (
        db.query(Repair)
        .filter(Repair.device_id == device.id)
        .order_by(Repair.created_at.asc())
        .all()
    )

    passport_repairs: List[PassportRepairItem] = []
    lifecycle_events: List[PassportLifecycleEvent] = []

    # Milestone 1: Purchase / Registration
    purchase_date = ensure_utc(device.purchase_date or device.created_at)
    lifecycle_events.append(
        PassportLifecycleEvent(
            event_type="PURCHASE",
            date=purchase_date,
            title="Initial Purchase & Registration",
            description=f"Registered as {device.brand} {device.model} ({device.category}) in {device.condition or 'Good'} condition.",
            cost=None,
            icon="🛍️",
        )
    )

    # Milestone 2: Diagnostics
    diagnostics = (
        db.query(Diagnostic)
        .filter(Diagnostic.device_id == device.id)
        .order_by(Diagnostic.created_at.asc())
        .all()
    )
    for diag in diagnostics:
        diag_date = ensure_utc(diag.created_at)
        lifecycle_events.append(
            PassportLifecycleEvent(
                event_type="DIAGNOSTIC",
                date=diag_date,
                title=f"Diagnostic Scan: {diag.reported_problem or 'Multi-point Inspection'}",
                description=f"Symptoms: {', '.join(diag.selected_symptoms or ['Hardware Scan'])}. Recommended Action: {diag.recommended_action or 'Inspection'}",
                cost=None,
                icon="🔍",
            )
        )

    # Latest warranty tracker
    latest_warranty_date: Optional[datetime] = None
    warranty_provider = "ReVivo Certified Guarantee"
    warranty_coverage_desc = "Standard parts and labor protection."

    for rep in repairs:
        # Find approved or latest quote
        approved_quote = (
            db.query(Quote)
            .filter(Quote.repair_id == rep.id, Quote.status == "APPROVED")
            .order_by(Quote.version.desc())
            .first()
        )
        if not approved_quote:
            approved_quote = (
                db.query(Quote)
                .filter(Quote.repair_id == rep.id)
                .order_by(Quote.version.desc())
                .first()
            )

        # Technician Info (Privacy Safe: business name & verified status only, NO personal contact details)
        tech_business = "ReVivo Certified Service Center"
        is_verified_tech = True
        if rep.technician_id:
            tech = db.query(TechnicianProfile).filter(TechnicianProfile.id == rep.technician_id).first()
            if tech and tech.business_name:
                tech_business = tech.business_name
                is_verified_tech = (tech.verification_status == "verified")

        # Parts Replaced extraction
        parts_list: List[str] = []
        if approved_quote:
            diag_text = approved_quote.diagnosis.lower()
            if "screen" in diag_text or "display" in diag_text or "oled" in diag_text:
                parts_list.append("OEM Display Assembly")
            if "battery" in diag_text:
                parts_list.append("High-Capacity Battery Pack")
            if "port" in diag_text or "charging" in diag_text:
                parts_list.append("USB-C Charging Sub-board")
            if "camera" in diag_text:
                parts_list.append("Primary Camera Sensor")
            if "keyboard" in diag_text:
                parts_list.append("Backlit Keyboard Module")
            if not parts_list:
                parts_list.append(approved_quote.diagnosis)
        elif rep.problem_description:
            parts_list.append("Hardware Component Service")

        cost = rep.quote_amount or (approved_quote.total_amount if approved_quote else 0.0)
        service_date = ensure_utc(rep.updated_at or rep.created_at)

        # Calculate service warranty
        warranty_duration_str = approved_quote.warranty_duration if approved_quote else "90 days warranty"
        warranty_days = parse_warranty_days(warranty_duration_str)
        service_warranty_end = service_date + timedelta(days=warranty_days)

        if latest_warranty_date is None or service_warranty_end > latest_warranty_date:
            latest_warranty_date = service_warranty_end
            warranty_provider = f"{tech_business} / ReVivo Network"
            warranty_coverage_desc = f"{warranty_duration_str} covering replaced components and labor."

        passport_repairs.append(
            PassportRepairItem(
                repair_id=rep.id,
                service_date=service_date,
                issue=rep.problem_description,
                parts_replaced=parts_list,
                technician_business=tech_business,
                is_verified_technician=is_verified_tech,
                repair_cost=round(cost, 2),
                service_warranty_valid_until=service_warranty_end,
                service_warranty_duration=warranty_duration_str,
                notes=rep.inspection_notes or (approved_quote.notes if approved_quote else None),
            )
        )

        lifecycle_events.append(
            PassportLifecycleEvent(
                event_type="REPAIR",
                date=service_date,
                title=f"Repair Completed: {', '.join(parts_list)}",
                description=f"Serviced by {tech_business}. Status: {rep.status.replace('_', ' ')}.",
                cost=cost,
                icon="🔧",
            )
        )

    # 3. Default 1-year purchase warranty fallback if no repair warranty
    if latest_warranty_date is None:
        initial_mfg_end = purchase_date + timedelta(days=365)
        latest_warranty_date = initial_mfg_end
        warranty_provider = f"{device.brand} Manufacturer Limited"
        warranty_coverage_desc = "Original 1-year manufacturer limited hardware warranty."

    # Active Warranty Computation
    is_warranty_active = latest_warranty_date > now
    days_left = max(0, (latest_warranty_date - now).days)
    warranty_status = "ACTIVE" if is_warranty_active else "EXPIRED"

    passport_warranty = PassportWarranty(
        is_active=is_warranty_active,
        status=warranty_status,
        valid_until=latest_warranty_date,
        provider=warranty_provider,
        days_remaining=days_left,
        coverage_details=warranty_coverage_desc,
    )

    # 4. Resale & Buyback Valuation Estimation
    base_value = 450.0 if device.category == "laptop" else 300.0
    if "apple" in device.brand.lower():
        base_value *= 1.4
    elif "samsung" in device.brand.lower() or "dell" in device.brand.lower():
        base_value *= 1.15

    # Premium for certified repair history with active warranty
    if is_warranty_active:
        base_value *= 1.1

    estimated_resale = round(base_value, 2)
    buyback_est = round(base_value * 0.82, 2)
    trade_in_val = round(base_value * 0.88, 2)

    resale_valuation = PassportResaleValuation(
        estimated_market_value=estimated_resale,
        revivo_buyback_estimate=buyback_est,
        trade_in_value=trade_in_val,
        currency="USD",
        currency_symbol="$",
        condition_grade="A - Certified Restored" if len(passport_repairs) > 0 else "B - Good",
    )

    # Sort lifecycle events reverse-chronologically
    lifecycle_events.sort(key=lambda e: e.date, reverse=True)

    health_status = "Certified Restored" if len(passport_repairs) > 0 else "Verified Active"
    if device.status == "repair":
        health_status = "In Active Service"

    return DevicePassportResponse(
        passport_id=f"REVIVO-DPP-{device.id:05d}",
        device_id=device.id,
        category=device.category,
        brand=device.brand,
        model=device.model,
        masked_identifier=masked_sn,
        purchase_date=purchase_date,
        initial_condition=device.condition or "Original",
        current_health_status=health_status,
        warranty=passport_warranty,
        repair_history=passport_repairs,
        lifecycle_timeline=lifecycle_events,
        resale_valuation=resale_valuation,
        qr_code_token=f"revivo://passport/{device.id}?key={masked_sn}",
        verified_at=now,
    )
