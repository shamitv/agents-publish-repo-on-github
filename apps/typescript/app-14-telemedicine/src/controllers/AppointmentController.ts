import { Request, Response } from "express";
import { AppointmentService } from "../services/AppointmentService";
import { AuthService } from "../services/AuthService";

export class AppointmentController {
  constructor(
    private readonly appointmentService: AppointmentService,
    private readonly authService: AuthService
  ) {}

  list = (req: Request, res: Response) => {
    const user = this.authService.requireUser(req.cookies?.token);
    if (!user) {
      return res.status(401).json({ message: "Access denied." });
    }
    return res.json({ appointments: this.appointmentService.listForUser(user) });
  };

  detail = (req: Request, res: Response) => {
    const user = this.authService.requireUser(req.cookies?.token);
    if (!user) {
      return res.status(401).json({ message: "Access denied." });
    }

    const appointment = this.appointmentService.getAppointmentDetail(Number(req.params.id));
    if (!appointment) {
      return res.status(404).json({ message: "Appointment not found." });
    }
    return res.json(appointment);
  };
}
