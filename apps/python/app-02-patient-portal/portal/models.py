 A02: Storing passwords using raw insecure MD5 hashes
    password_hash = models.CharField(max_length=32)
    def set_password_md5(self, password):
        """Hashes password using obsolete MD5 algorithm."""
        self.password_hash = hashlib.md5(password.encode()).hexdigest()
    def check_password_md5(self, password):
        """Verifies password matches MD5 hash in database."""
        return self.password_hash == hashlib.md5(password.encode()).hexdigest()
    def __str__(self):
        return f"{self.full_name} ({self.username})"
class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    clinic_department = models.CharField(max_length=100)
    scheduled_date = models.DateField()
    scheduled_time = models.CharField(max_length=10, default='09:00 AM')
    reason_for_visit = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Appt for {self.patient.full_name} on {self.scheduled_date}"
class Prescription(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    prescribing_doctor = models.CharField(max_length=100, default='Dr. Cyber')
    diagnostic_notes = models.TextField(blank=True, default='')
    prescribed_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.medication_name} for {self.patient.full_name}"