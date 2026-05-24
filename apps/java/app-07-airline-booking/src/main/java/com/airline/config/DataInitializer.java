package com.airline.config;

import com.airline.model.Booking;
import com.airline.model.Flight;
import com.airline.model.Passenger;
import com.airline.model.Seat;
import com.airline.repository.BookingRepository;
import com.airline.repository.FlightRepository;
import com.airline.repository.PassengerRepository;
import com.airline.repository.SeatRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private PassengerRepository passengerRepository;

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private SeatRepository seatRepository;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        if (passengerRepository.count() > 0) {
            return;
        }

        Passenger staff = Passenger.builder()
                .email("staff@airline.com")
                .passwordHash(passwordEncoder.encode("staff123"))
                .firstName("Airline")
                .lastName("Staff")
                .passportNumber("ST999999")
                .phone("+1-555-0199")
                .role("AIRLINE_STAFF")
                .build();

        Passenger john = Passenger.builder()
                .email("john@gmail.com")
                .passwordHash(passwordEncoder.encode("john123"))
                .firstName("John")
                .lastName("Doe")
                .passportNumber("US123456")
                .phone("+1-555-0101")
                .role("PASSENGER")
                .build();

        Passenger jane = Passenger.builder()
                .email("jane@gmail.com")
                .passwordHash(passwordEncoder.encode("jane123"))
                .firstName("Jane")
                .lastName("Smith")
                .passportNumber("US654321")
                .phone("+1-555-0102")
                .role("PASSENGER")
                .build();

        passengerRepository.save(staff);
        passengerRepository.save(john);
        passengerRepository.save(jane);

        List<Flight> flights = new ArrayList<>();
        
        flights.add(Flight.builder()
                .flightNumber("AA101")
                .airline("Apex Airlines")
                .origin("JFK")
                .destination("LAX")
                .departureTime(LocalDateTime.now().plusHours(12))
                .arrivalTime(LocalDateTime.now().plusHours(18))
                .price(new BigDecimal("350.00"))
                .totalSeats(30)
                .availableSeats(30)
                .build());

        flights.add(Flight.builder()
                .flightNumber("AA202")
                .airline("Apex Airlines")
                .origin("LHR")
                .destination("CDG")
                .departureTime(LocalDateTime.now().plusHours(20))
                .arrivalTime(LocalDateTime.now().plusHours(22))
                .price(new BigDecimal("120.00"))
                .totalSeats(30)
                .availableSeats(30)
                .build());

        flights.add(Flight.builder()
                .flightNumber("AA303")
                .airline("Apex Airlines")
                .origin("DXB")
                .destination("SIN")
                .departureTime(LocalDateTime.now().plusDays(2))
                .arrivalTime(LocalDateTime.now().plusDays(2).plusHours(8))
                .price(new BigDecimal("550.00"))
                .totalSeats(30)
                .availableSeats(30)
                .build());

        flights.add(Flight.builder()
                .flightNumber("AA404")
                .airline("Apex Airlines")
                .origin("HND")
                .destination("SFO")
                .departureTime(LocalDateTime.now().plusDays(3))
                .arrivalTime(LocalDateTime.now().plusDays(3).plusHours(9))
                .price(new BigDecimal("680.00"))
                .totalSeats(30)
                .availableSeats(30)
                .build());

        flights.add(Flight.builder()
                .flightNumber("AA505")
                .airline("Apex Airlines")
                .origin("SYD")
                .destination("AKL")
                .departureTime(LocalDateTime.now().plusDays(4))
                .arrivalTime(LocalDateTime.now().plusDays(4).plusHours(3))
                .price(new BigDecimal("180.00"))
                .totalSeats(30)
                .availableSeats(30)
                .build());

        flightRepository.saveAll(flights);

        // Row 1: First Class (1A-1E)
        // Row 2-3: Business Class (2A-3E)
        // Row 4-6: Economy Class (4A-6E)
        String[] seatLetters = {"A", "B", "C", "D", "E"};
        
        for (Flight f : flights) {
            List<Seat> seats = new ArrayList<>();
            for (int r = 1; r <= 6; r++) {
                String sClass = "ECONOMY";
                if (r == 1) sClass = "FIRST";
                else if (r <= 3) sClass = "BUSINESS";

                for (String letter : seatLetters) {
                    seats.add(Seat.builder()
                            .flight(f)
                            .seatNumber(r + letter)
                            .seatClass(sClass)
                            .isAvailable(true)
                            .build());
                }
            }
            seatRepository.saveAll(seats);
        }

        Flight aa101 = flightRepository.findAll().stream()
                .filter(f -> f.getFlightNumber().equals("AA101"))
                .findFirst().orElseThrow();
        
        Seat s1 = seatRepository.findByFlightId(aa101.getId()).stream()
                .filter(s -> s.getSeatNumber().equals("1A"))
                .findFirst().orElseThrow();
        s1.setIsAvailable(false);
        seatRepository.save(s1);
        aa101.setAvailableSeats(aa101.getAvailableSeats() - 1);
        flightRepository.save(aa101);

        Booking b1 = Booking.builder()
                .pnr("JFKJFK")
                .passenger(john)
                .flight(aa101)
                .seat(s1)
                .status("CONFIRMED")
                .bookedAt(LocalDateTime.now().minusDays(1))
                .paymentStatus("PAID")
                .build();
        bookingRepository.save(b1);

        Flight aa202 = flightRepository.findAll().stream()
                .filter(f -> f.getFlightNumber().equals("AA202"))
                .findFirst().orElseThrow();

        Seat s2 = seatRepository.findByFlightId(aa202.getId()).stream()
                .filter(s -> s.getSeatNumber().equals("2B"))
                .findFirst().orElseThrow();
        s2.setIsAvailable(false);
        seatRepository.save(s2);
        aa202.setAvailableSeats(aa202.getAvailableSeats() - 1);
        flightRepository.save(aa202);

        Booking b2 = Booking.builder()
                .pnr("LHRLHR")
                .passenger(jane)
                .flight(aa202)
                .seat(s2)
                .status("CONFIRMED")
                .bookedAt(LocalDateTime.now().minusHours(4))
                .paymentStatus("UNPAID")
                .build();
        bookingRepository.save(b2);
    }
}
