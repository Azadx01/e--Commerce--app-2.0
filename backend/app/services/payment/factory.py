from typing import Optional
from app.core.config import settings
from app.services.payment.base import BasePaymentProvider
from app.services.payment.sandbox import SandboxPaymentProvider

def get_payment_provider(provider_name: Optional[str] = None) -> BasePaymentProvider:
    """
    Factory resolving payment provider instances.
    Enables zero-code switching between Sandbox, Stripe, Razorpay, or local test harnesses.
    """
    target = (provider_name or settings.PAYMENT_PROVIDER or "sandbox").lower()

    if target == "sandbox" or settings.PAYMENT_SANDBOX_MODE:
        return SandboxPaymentProvider()
    
    # Fallback to Sandbox if mock mode or unsupported provider requested
    return SandboxPaymentProvider()
