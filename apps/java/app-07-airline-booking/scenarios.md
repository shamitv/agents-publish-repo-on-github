# Chained Vulnerability Scenarios - Airline Booking

## Chain: "Sequential PNR Enumeration -> Booking IDOR -> Stored XSS on Staff View"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | PNRs are generated as sequential values such as `BK000001` | Low | A04 | `PnrGenerator.java` -> `generate()` |
| 2 | `GET /api/bookings/{pnr}/boarding-summary` returns booking details without ownership validation | Medium | A01 | `BookingController.java` -> `getBoardingSummary()` |
| 3 | Passenger display HTML is rendered with `innerHTML` on the staff boarding page | Medium | A03 | `staff-boarding.html` |

**Attack narrative**: The attacker registers with a script payload in their passenger name, enumerates valid PNRs, and waits for staff to load the boarding summary. The staff UI renders the API-provided passenger HTML with `innerHTML`, executing the script.

**Combined Impact**: Staff account takeover through stored XSS.

---

## Chain: "Predictable Seat Hold References -> Hold Ownership Bypass -> Unauthorized Hold Confirmation"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Seat hold references use predictable values such as `HOLD000101` | Low | A04 | `HoldRefGenerator.java` -> `generate()` |
| 2 | Hold read and seat-change operations skip ownership checks | Medium | A01 | `SeatHoldService.java` -> `getHoldByRef()` / `changeHeldSeat()` |
| 3 | Hold confirmation skips owner and payment verification | Medium | A04 | `SeatHoldService.java` -> `confirmHold()` |

**Attack narrative**: The attacker guesses a victim hold reference, reads the hold, changes the held seat, and confirms the hold as their own booking.

**Combined Impact**: Unauthorized seat inventory and booking-record modification.

---

Ground truth vulnerability data is maintained in [.vulns](.vulns).
