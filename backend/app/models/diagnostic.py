from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_problem = Column(Text, nullable=True)
    selected_symptoms = Column(JSON, nullable=False)
    image_references = Column(JSON, nullable=True, default=list)
    diagnosis_result = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    engine_version = Column(String(50), nullable=False, default="v1.0-rule-based")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("Device", back_populates="diagnostics")

    @property
    def possible_issue(self) -> str:
        if isinstance(self.diagnosis_result, dict):
            return self.diagnosis_result.get("possible_issue", "")
        return ""

    @property
    def estimated_severity(self) -> str:
        if isinstance(self.diagnosis_result, dict):
            return self.diagnosis_result.get("estimated_severity", "")
        return ""

    @property
    def recommended_next_action(self) -> str:
        if isinstance(self.diagnosis_result, dict):
            return self.diagnosis_result.get("recommended_next_action", "")
        return ""

    @property
    def recommended_action(self) -> str:
        return self.recommended_next_action

    @property
    def requirement_for_technician_inspection(self) -> bool:
        if isinstance(self.diagnosis_result, dict):
            return self.diagnosis_result.get("requirement_for_technician_inspection", False)
        return False

    @property
    def requires_technician_inspection(self) -> bool:
        return self.requirement_for_technician_inspection

    @property
    def disclaimer(self) -> str:
        if isinstance(self.diagnosis_result, dict):
            return self.diagnosis_result.get(
                "disclaimer",
                "This assessment is rule-based and advisory only. It does not provide guaranteed diagnosis or certainty. Physical technician inspection is recommended."
            )
        return "This assessment is rule-based and advisory only. It does not provide guaranteed diagnosis or certainty."
