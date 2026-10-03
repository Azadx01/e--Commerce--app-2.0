from typing import List, Optional, Dict, Any
from enum import Enum

class SymptomCategory(str, Enum):
    BATTERY = "Battery"
    SCREEN = "Screen"
    CHARGING = "Charging"
    HEATING = "Heating"
    PERFORMANCE = "Performance"
    KEYBOARD = "Keyboard"
    CAMERA = "Camera"
    SPEAKER = "Speaker"
    NETWORK = "Network"
    OTHER = "Other"

ENGINE_VERSION = "v1.0-rule-based"

SYSTEM_DISCLAIMER = (
    "This automated assessment is rule-based and advisory only. It does not provide "
    "guaranteed diagnosis or absolute certainty. For conclusive hardware evaluation, "
    "a hands-on physical inspection by a certified technician is recommended."
)

def evaluate_device_diagnosis(
    selected_symptoms: List[str],
    reported_problem: Optional[str] = None,
    image_references: Optional[List[str]] = None,
    device_category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Structured Rule-Based Diagnosis Engine for Customer Device Triage.
    Evaluates:
      - possible_issue
      - estimated_severity ('Low', 'Medium', 'High', 'Critical')
      - recommended_next_action
      - confidence (between 0.50 and 0.92, never claimed as absolute certainty)
      - requirement_for_technician_inspection (bool)
      - engine_version
      - disclaimer
    """
    symptoms_set = {s.strip().title() for s in selected_symptoms}
    prob_lower = (reported_problem or "").lower()
    has_images = bool(image_references and len(image_references) > 0)
    image_count = len(image_references) if image_references else 0

    # 1. Critical safety hazard checks in reported problem
    liquid_keywords = ["water", "liquid", "spill", "dropped in pool", "submerged", "toilet", "coffee", "juice", "wet"]
    hazard_keywords = ["smoke", "spark", "swollen", "bulging", "burning smell", "fire", "exploded", "popped", "battery expanding"]

    if any(k in prob_lower for k in hazard_keywords):
        return {
            "possible_issue": "Suspected Battery Thermal Runaway or Electrical Short Hazard",
            "estimated_severity": "Critical",
            "recommended_next_action": (
                "IMMEDIATE ACTION REQUIRED: Disconnect all chargers immediately. "
                "Do not puncture, squeeze, or power on the device. Store in a cool, fireproof area "
                "and transport safely to a certified service center for hazardous handling."
            ),
            "confidence": 0.92,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Critical thermal/electrical hazard indicators detected in user description."
        }

    if any(k in prob_lower for k in liquid_keywords):
        return {
            "possible_issue": "Suspected Liquid Ingress & Internal Circuit Corrosion",
            "estimated_severity": "Critical",
            "recommended_next_action": (
                "Do NOT attempt to power on or plug into a charger. Do NOT put device in rice. "
                "Keep device upright in a dry environment and bring immediately to a technician "
                "for urgent disassembly, battery disconnect, and ultrasonic PCB cleaning."
            ),
            "confidence": 0.90,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Moisture exposure detected. Swift professional intervention prevents irreversible motherboard oxidation."
        }

    # 2. Multi-Symptom Rule Combinations
    if "Battery" in symptoms_set and "Heating" in symptoms_set:
        return {
            "possible_issue": "Suspected Severe Battery Cell Degradation or Internal Resistance Anomaly",
            "estimated_severity": "High",
            "recommended_next_action": (
                "Cease demanding tasks and unplug any fast charger. Monitor for physical swelling. "
                "Schedule a technician inspection to test battery voltage stability and thermal sensors."
            ),
            "confidence": 0.88,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": f"Combined battery and thermal anomalies detected.{' Attached images logged for inspection.' if has_images else ''}"
        }

    if "Battery" in symptoms_set and "Charging" in symptoms_set:
        return {
            "possible_issue": "Suspected Power Management IC (PMIC) Fault or Worn Battery Cell",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Test charging with a known-good certified cable and lower-wattage adapter. "
                "If device remains unresponsive or battery percentage jumps erratically, technician diagnosis is required."
            ),
            "confidence": 0.85,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Power delivery chain instability detected across battery and charging interfaces."
        }

    if "Heating" in symptoms_set and "Performance" in symptoms_set:
        return {
            "possible_issue": "Suspected Thermal Throttling from Inefficient Heat Dissipation or Process Overload",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Close heavy background applications, verify available storage space, and restart the device. "
                "If heating continues under light usage, technician servicing is recommended for thermal paste renewal or fan cleaning."
            ),
            "confidence": 0.82,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Processor thermal regulation safeguards appear to be throttling system throughput."
        }

    if "Screen" in symptoms_set and ("Battery" in symptoms_set or "Charging" in symptoms_set):
        return {
            "possible_issue": "Suspected Inconsistent Display Power Rail or Backlight Voltage Fluctuation",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Observe if screen flickering coincides with charging or low battery states. "
                "A technician inspection is recommended to check mainboard voltage regulators."
            ),
            "confidence": 0.78,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Interdependent display and power rail symptoms detected."
        }

    # 3. Single / Dominant Symptom Rules
    if "Screen" in symptoms_set:
        screen_damage_keywords = ["crack", "shatter", "black", "blank", "flicker", "lines", "bleed", "dead pixel", "ghost touch", "touch"]
        is_damage_mentioned = any(k in prob_lower for k in screen_damage_keywords) or has_images
        if is_damage_mentioned:
            return {
                "possible_issue": "Suspected Display Panel Fracture, Digitizer Failure, or OLED/LCD Damage",
                "estimated_severity": "High",
                "recommended_next_action": (
                    "Back up device data immediately if touch functionality remains. "
                    "Avoid applying pressure to prevent micro-fracture propagation. "
                    "Technician replacement of display assembly is recommended."
                ),
                "confidence": 0.88,
                "requirement_for_technician_inspection": True,
                "engine_version": ENGINE_VERSION,
                "disclaimer": SYSTEM_DISCLAIMER,
                "notes": f"Hardware display panel anomaly indicated.{' Optional image uploaded for damage verification.' if has_images else ''}"
            }
        return {
            "possible_issue": "Suspected Display Panel or Flex Ribbon Connection Disruption",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Perform a forced reboot to eliminate software rendering bugs. "
                "If display artifacts or unresponsive zones persist, technician inspection is required."
            ),
            "confidence": 0.78,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Preliminary display diagnosis."
        }

    if "Battery" in symptoms_set:
        return {
            "possible_issue": "Suspected Chemical Battery Aging or Diminished Charge Capacity",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Review battery health percentage in system settings. Perform a complete calibration cycle. "
                "If maximum capacity is below 80% or unexpected shutdowns occur, technician replacement is recommended."
            ),
            "confidence": 0.82,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Electrochemical capacity degradation pattern."
        }

    if "Charging" in symptoms_set:
        return {
            "possible_issue": "Suspected Charging Port Obstruction, Pin Corrosion, or I/O Board Fault",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Gently inspect the charging port with adequate lighting for compacted lint or debris. "
                "Clean carefully with a non-conductive, antistatic tool. Try an alternate OEM cable. "
                "If charging remains intermittent, bring to a technician for port testing."
            ),
            "confidence": 0.80,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Physical port or charging circuit connection irregularity."
        }

    if "Heating" in symptoms_set:
        return {
            "possible_issue": "Suspected Elevated Thermal Output or Suboptimal Thermal Dissipation",
            "estimated_severity": "Medium",
            "recommended_next_action": (
                "Remove protective cases during charging and avoid direct sunlight. "
                "Check background battery and CPU consumption. If high surface heat persists during idle, "
                "technician inspection is advised."
            ),
            "confidence": 0.76,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Thermal dissipation warning."
        }

    if "Performance" in symptoms_set:
        return {
            "possible_issue": "Suspected Memory Pressure, Flash Storage Congestion, or Software Background Throttling",
            "estimated_severity": "Low",
            "recommended_next_action": (
                "Ensure at least 15-20% free storage space. Clear application cache and restart the system. "
                "If slowness or freezing continues after clean restore, technician hardware diagnostic is recommended."
            ),
            "confidence": 0.72,
            "requirement_for_technician_inspection": False,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Primary software troubleshooting recommended before hardware escalation."
        }

    if "Keyboard" in symptoms_set:
        return {
            "possible_issue": "Suspected Switch Contact Degradation, Debris Jamming, or Ribbon Controller Disconnection",
            "estimated_severity": "Low",
            "recommended_next_action": (
                "Use compressed air to dislodge particulate debris from under keycaps. "
                "Test keystrokes with an input testing utility. If entire key clusters fail, "
                "technician inspection for top-case/keyboard replacement is required."
            ),
            "confidence": 0.80,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Input mechanism mechanical/electrical contact fault."
        }

    if "Camera" in symptoms_set:
        return {
            "possible_issue": "Suspected Image Sensor Defect, OIS Actuator Failure, or Lens Alignment Issue",
            "estimated_severity": "Low",
            "recommended_next_action": (
                "Clean the protective outer lens cover. Test across multiple photographic apps. "
                "If shutter clicks/buzzes, focus hunts continuously, or view remains blank, technician replacement is needed."
            ),
            "confidence": 0.78,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Optical module diagnostic."
        }

    if "Speaker" in symptoms_set:
        return {
            "possible_issue": "Suspected Speaker Diaphragm Tearing, Grille Dust Ingress, or Audio Amplifier IC Fault",
            "estimated_severity": "Low",
            "recommended_next_action": (
                "Clean speaker acoustic grilles gently with a dry, soft bristle brush. "
                "Test audio across different volume levels and frequencies. If audio distorts, buzzes, or is inaudible, "
                "technician inspection is recommended."
            ),
            "confidence": 0.78,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "Acoustic transducer diagnostic."
        }

    if "Network" in symptoms_set:
        return {
            "possible_issue": "Suspected Wireless Antenna Attenuation, Baseband Glitch, or Wi-Fi/Bluetooth Module Fault",
            "estimated_severity": "Low",
            "recommended_next_action": (
                "Reset network settings, toggle Airplane mode, and re-insert the SIM card. "
                "If the device fails to scan or connect to any known wireless networks, hardware antenna inspection is advised."
            ),
            "confidence": 0.75,
            "requirement_for_technician_inspection": True,
            "engine_version": ENGINE_VERSION,
            "disclaimer": SYSTEM_DISCLAIMER,
            "notes": "RF antenna and network controller diagnostic."
        }

    # 4. Fallback / Other
    return {
        "possible_issue": "Suspected Generalized Hardware or System Level Anomaly",
        "estimated_severity": "Medium",
        "recommended_next_action": (
            "Document specific error codes or failure triggers. Back up critical data. "
            "A comprehensive physical inspection and diagnostic scan by a certified technician is recommended."
        ),
        "confidence": 0.55,
        "requirement_for_technician_inspection": True,
        "engine_version": ENGINE_VERSION,
        "disclaimer": SYSTEM_DISCLAIMER,
        "notes": f"General triage assessment.{' Visual references queued for technician.' if has_images else ''}"
    }
