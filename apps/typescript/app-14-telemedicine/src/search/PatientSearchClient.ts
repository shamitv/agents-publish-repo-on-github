import { AppConfig } from "../config/appConfig";
import { Appointment } from "../models/Appointment";

export class PatientSearchClient {
  constructor(private readonly config: AppConfig) {}

  indexAppointment(_appointment: Appointment) {
    return {
      target: this.config.patientSearchUrl,
      indexed: true
    };
  }
}
