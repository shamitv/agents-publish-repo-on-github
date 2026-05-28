import { InMemoryMedicalDatabase } from "../db/InMemoryMedicalDatabase";

export class AppointmentRepository {
  constructor(private readonly database: InMemoryMedicalDatabase) {}

  findForPatient(patientId: number) {
    return this.database.appointments.filter((appointment) => appointment.patientId === patientId);
  }

  findForDoctor(doctorId: number) {
    return this.database.appointments.filter((appointment) => appointment.doctorId === doctorId);
  }

  findAll() {
    return [...this.database.appointments];
  }

  findById(id: number) {
    return this.database.appointments.find((appointment) => appointment.id === id);
  }
}
