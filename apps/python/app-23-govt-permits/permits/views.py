import os
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import Permit, Document

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {'username': user.username, 'is_staff': user.is_staff}
            })
        return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})

def permit_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    # Decoy: Proper scoped queries — regular citizens can only see their own permits,
    # while reviewers (staff) can see all permits.
    if request.user.is_staff:
        permits = Permit.objects.all()
    else:
        permits = Permit.objects.filter(applicant=request.user)

    data = [{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'applicant': p.applicant.username,
        'status': p.status,
        'submitted_at': p.submitted_at
    } for p in permits]
    return JsonResponse({'permits': data})

# VULNERABILITY A01: IDOR on permit details.
# Any authenticated user can view any permit application by ID.
# No check is performed to verify if the requesting user is the applicant or staff/reviewer.
def permit_detail(request, permit_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    try:
        permit = Permit.objects.get(id=permit_id)
    except Permit.DoesNotExist:
        return JsonResponse({'message': 'Permit not found'}, status=404)

    documents = [{
        'id': doc.id,
        'file_url': doc.file.url,
        'uploaded_at': doc.uploaded_at
    } for doc in permit.documents.all()]

    return JsonResponse({
        'id': permit.id,
        'title': permit.title,
        'description': permit.description,
        'applicant': permit.applicant.username,
        'status': permit.status,
        'submitted_at': permit.submitted_at,
        'documents': documents
    })

# VULNERABILITY A08: Software and Data Integrity Failures (Unrestricted File Upload).
# CHAIN LINK 2 (chain-01): The upload endpoint accepts any file type (e.g. .py, .sh, executable files)
# and saves it to a predictable directory under media root. Since DEBUG=True is active,
# static files helper in urls.py will serve these files, enabling the attacker to execute uploaded files.
@csrf_exempt
def upload_document(request, permit_id):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)

    try:
        permit = Permit.objects.get(id=permit_id)
    except Permit.DoesNotExist:
        return JsonResponse({'message': 'Permit not found'}, status=404)

    if request.method == 'POST' and request.FILES.get('document'):
        uploaded_file = request.FILES['document']
        
        # Unrestricted upload: no validation on file name, extension or MIME type.
        fs = FileSystemStorage()
        filename = fs.save(f"documents/{uploaded_file.name}", uploaded_file)
        
        # Save to DB
        doc = Document.objects.create(permit=permit, file=filename)
        
        return JsonResponse({
            'success': True,
            'document_id': doc.id,
            'file_name': uploaded_file.name,
            'file_url': doc.file.url
        })
    
    return JsonResponse({'message': 'Bad request or missing file'}, status=400)

@csrf_exempt
def approve_permit(request, permit_id):
    # Decoy: Proper authorization check on administrative actions (reviewer only)
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Unauthenticated'}, status=401)
    
    if not request.user.is_staff:
        return JsonResponse({'message': 'Forbidden: Reviewer privilege required'}, status=403)

    try:
        permit = Permit.objects.get(id=permit_id)
    except Permit.DoesNotExist:
        return JsonResponse({'message': 'Permit not found'}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status', 'APPROVED')
        except ValueError:
            status = 'APPROVED'
            
        permit.status = status
        permit.save()
        return JsonResponse({'success': True, 'permit_id': permit.id, 'status': permit.status})
        
    return JsonResponse({'message': 'Method not allowed'}, status=405)
