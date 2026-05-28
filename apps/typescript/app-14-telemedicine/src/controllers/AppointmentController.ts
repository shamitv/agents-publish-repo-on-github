import { Request, Response } from "express";
import { AppointmentService } from "../services/AppointmentService";
import { AuthService } from "../services/AuthService";

export class AppointmentController {
  constructor(
    private readonly appointmentService: AppointmentService,
    private readonly authService: AuthService
  ) {}

  list = async (req: Request, res: Response) => {
    const user = this.authService.requireUser(req.cookies?.token);
    if (!user) {
      return res.status(401).json({ message: "Access denied." });
    }
    const appointments = await this.appointmentService.listForUser(user);
    return res.json({ appointments });
  };

  detail = async (req: Request, res: Response) => {
    const user = this.authService.requireUser(req.cookies?.token);
    if (!user) {
      return res.status(401).json({ message: "Access denied." });
    }

    const appointment = await this.appointmentService.getAppointmentDetail(Number(req.params.id));
    if (!appointment) {
      return res.status(404).json({ message: "Appointment not found." });
    }
    return res.json(appointment);
  };
}
