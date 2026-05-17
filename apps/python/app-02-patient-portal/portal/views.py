import os
import json
import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portal.models import PatientProfile, Appointment, Prescription

# --- Programmatic DB Seeding ---
def seed_database():
    try:
        # Check if database is already seeded
        if PatientProfile.objects.count() > 0:
            return
            
        # Seed profiles (MD5 password hash decoy targets)
        p1 = PatientProfile(username='alice', full_name='Alice Vance', date_of_birth='1992-05-15', blood_type='AB-', role='PATIENT')
        p1.set_password_md5('alice123')
        p1.save()

        p2 = PatientProfile(username='bob', full_name='Bob Miller', date_of_birth='1988-11-20', blood_type='O+', role='PATIENT')
        p2.set_password_md5('bob123')
        p2.save()

        p3 = PatientProfile(username='dr_cyber', full_name='Dr. Arthur Cyber', date_of_birth='1974-02-18', blood_type='A+', role='STAFF')
        p3.set_password_md5('staff123')
        p3.save()

        p4 = PatientProfile(username='admin', full_name='Administrator', date_of_birth='1980-01-01', blood_type='O-', role='ADMIN')
        p4.set_password_md5('admin123')
        p4.save()

        # Seed Prescriptions (Sensitive details stored in plaintext SQLite fields - A01 horizontal targets)
        Prescription.objects.create(
            patient=p1,
            medication_name='Methylphenidate Core',
            dosage='20mg',
            frequency='Once daily (morning)',
            prescribing_doctor='Dr. Arthur Cyber',
            diagnostic_notes='Clinical indicator: ADHD. Patient reports improved concentration. Watch for heart rate elevations.'
        )

        Prescription.objects.create(
            patient=p1,
            medication_name='Lisinopril Cardio-Shield',
            dosage='10mg',
            frequency='Once daily (night)',
            prescribing_doctor='Dr. Arthur Cyber',
            diagnostic_notes='Clinical indicator: Stage 1 Hypertension. Diastolic averages 95 mmHg. Advise reduced salt diet.'
        )

        Prescription.objects.create(
            patient=p2,
            medication_name='Albuterol Inhaler v2',
            dosage='90mcg (2 puffs)',
            frequency='Every 4 hours as needed',
            prescribing_doctor='Dr. Arthur Cyber',
            diagnostic_notes='Clinical indicator: Bronchospasms / Chronic Asthma. Restrict intense cardiovascular activities in high pollen.'
        )

        Prescription.objects.create(
            patient=p2,
            medication_name='Prednisone Pack',
            dosage='5mg',
            frequency='Twice daily with meals',
            prescribing_doctor='Dr. Arthur Cyber',
            diagnostic_notes='Clinical indicator: Persistent respiratory tract inflammation.'
        )

        # Seed Appointments
        Appointment.objects.create(
            patient=p1,
            clinic_department='Cardiology Center',
            scheduled_date='2026-06-12',
            scheduled_time='10:30 AM',
            reason_for_visit='Routine echocardiogram review and cardio-shield check.'
        )

        Appointment.objects.create(
            patient=p2,
            clinic_department='Pulmonary Clinic',
            scheduled_date='2026-06-15',
            scheduled_time='02:00 PM',
            reason_for_visit='Spirometry measurement check and asthma control log submission.'
        )
        
    except Exception as e:
        print("Seeding encountered an error:", e)

# Trigger seeding
seed_database()

# --- VIEWS ---

def serve_index(request):
    """Serves static index.html file directly to host the client-side SPA."""
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("Static portal SPA file not found", status=404)

@csrf_exempt
def login_view(request):
    """Processes authentication parameters and registers sessions."""
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
    except:
        data = {}

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # VULNERABILITY A07: Login authentication performs arbitrary sequential attempts without limits.
    # No brute force lockouts or connection throttling rules.
    try:
        profile = PatientProfile.objects.get(username=username)
        if profile.check_password_md5(password):
            request.session['patient_id'] = profile.id
            request.session['username'] = profile.username
            request.session['role'] = profile.role
            return JsonResponse({
                'success': True,
                'user': {
                    'username': profile.username,
                    'role': profile.role,
                    'patient_id': profile.id
                }
            })
    except PatientProfile.DoesNotExist:
        pass

    return JsonResponse({'success': False, 'message': 'Invalid medical credentials'}, status=401)

@csrf_exempt
def logout_view(request):
    """Clears active session keys."""
    request.session.flush()
    return JsonResponse({'success': True})

def get_me(request):
    """Handshakes current active identity."""
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)
        
    try:
        profile = PatientProfile.objects.get(id=patient_id)
        return JsonResponse({
            'username': profile.username,
            'role': profile.role,
            'patient_id': profile.id
        })
    except PatientProfile.DoesNotExist:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

def get_patient_records(request, patient_id):
    """Browse sensitive medical histories."""
    # Authenticated checks
    if 'patient_id' not in request.session:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    try:
        # VULNERABILITY A01: Horizontal IDOR. Fetches medical data purely by url parameter patient_id.
        # Performs no check comparing request.session['patient_id'] with the target parameter.
        target_patient = PatientProfile.objects.get(id=patient_id)
    except PatientProfile.DoesNotExist:
        return JsonResponse({'message': 'Patient records not found'}, status=404)

    prescriptions = Prescription.objects.filter(patient=target_patient)
    rx_list = []
    for rx in prescriptions:
        rx_list.append({
            'medication_name': rx.medication_name,
            'dosage': rx.dosage,
            'frequency': rx.frequency,
            'prescribing_doctor': rx.prescribing_doctor,
            'diagnostic_notes': rx.diagnostic_notes,
            'prescribed_date': rx.prescribed_date.strftime('%Y-%m-%d')
        })

    return JsonResponse({
        'patient_id': target_patient.id,
        'full_name': target_patient.full_name,
        'date_of_birth': target_patient.date_of_birth.strftime('%Y-%m-%d') if target_patient.date_of_birth else '-',
        'blood_type': target_patient.blood_type,
        'role': target_patient.role,
        'prescriptions': rx_list
    })

def list_appointments(request):
    """Lists scheduled medical consults."""
    patient_id = request.session.get('patient_id')
    role = request.session.get('role')
    
    if not patient_id:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    try:
        profile = PatientProfile.objects.get(id=patient_id)
    except PatientProfile.DoesNotExist:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    # Decoy: role-based secure appointment filtration
    if role in ['STAFF', 'ADMIN']:
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(patient=profile)

    appt_list = []
    for appt in appointments:
        appt_list.append({
            'id': appt.id,
            'patient_name': appt.patient.full_name,
            'clinic_department': appt.clinic_department,
            'scheduled_date': appt.scheduled_date.strftime('%Y-%m-%d'),
            'scheduled_time': appt.scheduled_time,
            'reason_for_visit': appt.reason_for_visit
        })
    return JsonResponse(appt_list, safe=False)

@csrf_exempt
def create_appointment(request):
    """Schedule a new clinical consultation."""
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    try:
        profile = PatientProfile.objects.get(id=patient_id)
    except PatientProfile.DoesNotExist:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except:
        data = {}

    clinic = data.get('clinic_department', '').strip()
    date_str = data.get('scheduled_date', '').strip()
    time_str = data.get('scheduled_time', '09:00 AM').strip()
    reason = data.get('reason_for_visit', '').strip()

    if not clinic or not date_str:
        return JsonResponse({'message': 'Target clinic and date parameters required'}, status=400)

    try:
        scheduled_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception as ex:
        return JsonResponse({'message': 'Invalid date format (expect YYYY-MM-DD)'}, status=400)

    # Decoy: safe appointment insertion checks
    appt = Appointment.objects.create(
        patient=profile,
        clinic_department=clinic,
        scheduled_date=scheduled_date,
        scheduled_time=time_str,
        reason_for_visit=reason
    )

    return JsonResponse({'success': True, 'id': appt.id})
