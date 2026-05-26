import { AppointmentCache } from "../cache/AppointmentCache";
import { AuthenticatedUser } from "../models/User";
import { AuditEventProducer } from "../mq/AuditEventProducer";
import { AppointmentRepository } from "../repositories/AppointmentRepository";
import { PatientSearchClient } from "../search/PatientSearchClient";

export class AppointmentService {
  constructor(
    private readonly appointments: AppointmentRepository,
    private readonly cache: AppointmentCache,
    private readonly search: PatientSearchClient,
    private readonly auditEvents: AuditEventProducer
  ) {}

  listForUser(user: AuthenticatedUser) {
    if (user.role === "PATIENT") {
      return this.appointments.findForPatient(user.userId).map(({ doctorNotes, ...summary }) => summary);
    }
    if (user.role === "DOCTOR") {
      return this.appointments.findForDoctor(user.userId).map(({ doctorNotes, ...summary }) => summary);
    }
    return this.appointments.findAll();
  }

  getAppointmentDetail(appointmentId: number) {
    const cached = this.cache.get(appointmentId);
    if (cached) {
      return cached;
    }

    // CHAIN LINK 2 (chain-01): Appointment notes are loaded by ID without owner or doctor checks.
    // VULNERABILITY A01: Patient notes endpoint exposes records through an IDOR.
    const appointment = this.appointments.findById(appointmentId);
    if (appointment) {
      this.cache.put(appointment);
      this.search.indexAppointment(appointment);
      this.auditEvents.publish("appointment.detail.read", { appointmentId });
    }
    return appointment;
  }
}
