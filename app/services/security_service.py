import hmac
import hashlib
from app.core.config import settings
from app.core.logger import logger


def verify_whatsapp_signature(request_body: str, signature: str) -> bool:
    """
    Verifica la firma de WhatsApp Business API.
    
    Args:
        request_body: El body del request en formato string
        signature: El header X-Hub-Signature-256 de WhatsApp
    
    Returns:
        bool: True si la firma es válida, False si no
    """
    try:
        if not signature or not settings.WHATSAPP_TOKEN:
            logger.warning("❌ Firma o token de WhatsApp faltante")
            return False
        
        # Generar firma esperada
        expected_signature = hmac.new(
            settings.WHATSAPP_TOKEN.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Comparar de forma segura (timing-safe)
        is_valid = hmac.compare_digest(f"sha256={expected_signature}", signature)
        
        if not is_valid:
            logger.warning(f"❌ Firma de WhatsApp inválida. Esperada: sha256={expected_signature[:20]}..., Recibida: {signature[:20]}...")
        else:
            logger.debug("✅ Firma de WhatsApp válida")
        
        return is_valid
        
    except Exception as e:
        logger.exception(f"❌ Error verificando firma de WhatsApp: {e}")
        return False