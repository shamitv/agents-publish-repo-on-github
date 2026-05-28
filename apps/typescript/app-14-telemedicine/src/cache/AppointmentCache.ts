import { Appointment } from "../models/Appointment";

export class AppointmentCache {
  private readonly appointments = new Map<number, Appointment>();

  get(id: number) {
    return this.appointments.get(id);
  }

  put(appointment: Appointment) {
    this.appointments.set(appointment.id, appointment);
  }

  clear(id: number) {
    this.appointments.delete(id);
  }
}
