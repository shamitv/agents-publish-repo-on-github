import bcrypt from "bcryptjs";
import { Appointment } from "../models/Appointment";
import { User } from "../models/User";

const hash = (password: string) => bcrypt.hashSync(password, bcrypt.genSaltSync(10));

export class InMemoryMedicalDatabase {
  readonly users: User[] = [
    { id: 1, username: "john_patient", passwordHash: hash("john_pass_123"), role: "PATIENT" },
    { id: 2, username: "jane_patient", passwordHash: hash("jane_pass_456"), role: "PATIENT" },
    { id: 3, username: "dr_house", passwordHash: hash("house_pass_789"), role: "DOCTOR" },
    { id: 4, username: "admin", passwordHash: hash("admin_pass_2026"), role: "ADMIN" }
  ];

  readonly appointments: Appointment[] = [
    {
      id: 1,
      patientId: 1,
      doctorId: 3,
      date: "2026-06-01",
      status: "SCHEDULED",
      doctorNotes: "Patient john exhibits mild seasonal allergy symptoms. Prescribed Claritin."
    },
    {
      id: 2,
      patientId: 2,
      doctorId: 3,
      date: "2026-06-02",
      status: "SCHEDULED",
      doctorNotes: "Patient jane reports chronic back pain. Referred to physical therapy."
    }
  ];

  nextUserId() {
    return Math.max(...this.users.map((user) => user.id), 0) + 1;
  }
}
