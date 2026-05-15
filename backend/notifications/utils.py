from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from parents.models import Baby
from vaccinations.models import BabyVaccine
from appointments.models import Appointment

def send_vaccine_reminders():
    """Finds vaccines due in the next 3 days and sends email to parents."""
    today = timezone.now().date()
    target_date = today + timedelta(days=3)
    
    # Simple logic: check vaccines that are not completed and are due soon
    pending_vax = BabyVaccine.objects.filter(completed=False).select_related('baby', 'vaccine', 'baby__parent')
    
    sent_count = 0
    for v in pending_vax:
        due_date = v.baby.dob + timedelta(days=v.vaccine.due_days)
        if today <= due_date <= target_date:
            subject = f"Upcoming Vaccine Reminder: {v.vaccine.name} for {v.baby.name}"
            message = f"Hello,\n\nThis is a reminder from BabyBloom that {v.baby.name} is due for the {v.vaccine.name} vaccine on {due_date}.\n\nPlease book an appointment with your doctor soon.\n\nBest regards,\nThe BabyBloom Team"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [v.baby.parent.email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send email to {v.baby.parent.email}: {e}")
    
    return sent_count

def send_appointment_reminders():
    """Finds appointments for tomorrow and sends email."""
    tomorrow = timezone.now().date() + timedelta(days=1)
    appts = Appointment.objects.filter(date=tomorrow).select_related('baby', 'baby__parent', 'doctor__user')
    
    sent_count = 0
    for a in appts:
        subject = f"Appointment Reminder: Tomorrow with Dr. {a.doctor.user.username}"
        message = f"Hello,\n\nThis is a reminder for your appointment tomorrow ({tomorrow}) at BabyBloom for {a.baby.name}.\n\nDoctor: Dr. {a.doctor.user.username}\nStatus: {a.status}\n\nWe look forward to seeing you.\n\nBest regards,\nThe BabyBloom Team"
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [a.baby.parent.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send appointment reminder to {a.baby.parent.email}: {e}")
            
    return sent_count

def send_welcome_email(user):
    """Sends a welcome email to a newly registered parent."""
    subject = "Welcome to BabyBloom! 👶"
    message = f"Hello {user.username},\n\nWelcome to BabyBloom! We are thrilled to have you join our community.\n\nOur platform is designed to help you track your baby's growth, manage vaccination schedules, and connect with clinical experts easily.\n\nTo get started, please add your baby's profile in the dashboard.\n\nBest regards,\nThe BabyBloom Team"
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False, # Changed to False so we can see errors in console
        )
        print(f"✅ Welcome email successfully sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Welcome email failed for {user.email}: {e}")
        return False
