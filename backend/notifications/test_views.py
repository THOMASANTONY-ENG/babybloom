from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import traceback

@api_view(['GET'])
@permission_classes([IsAdminUser])
def test_email_config(request):
    """Diagnostic tool to test Gmail SMTP settings and see the raw error."""
    recipient = request.GET.get('email', settings.EMAIL_HOST_USER)
    subject = "BabyBloom Email Test 🧪"
    message = "If you see this, your Gmail SMTP settings are working perfectly!"
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient],
            fail_silently=False, # We want to see the error!
        )
        return Response({
            "status": "success",
            "message": f"Test email sent successfully to {recipient}!",
            "config_used": {
                "host": settings.EMAIL_HOST,
                "user": settings.EMAIL_HOST_USER,
                "port": settings.EMAIL_PORT
            }
        })
    except Exception as e:
        return Response({
            "status": "failed",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "hint": "Check if your Gmail App Password is correct and 2FA is enabled."
        }, status=500)
