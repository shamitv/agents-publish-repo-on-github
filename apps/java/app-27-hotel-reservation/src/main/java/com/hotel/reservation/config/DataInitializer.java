package com.hotel.reservation.config;
import com.hotel.reservation.model.*;
import com.hotel.reservation.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDate;
@Component
public class DataInitializer implements CommandLineRunner {
    private final UserRepository userRepository;
    private final GuestRepository guestRepository;
    private final RoomRepository roomRepository;
    private final RoomRateRepository roomRateRepository;
    private final ReservationRepository reservationRepository;
    private final PasswordEncoder passwordEncoder;
    public DataInitializer(UserRepository userRepository, GuestRepository guestRepository,
                           RoomRepository roomRepository, RoomRateRepository roomRateRepository,
                           ReservationRepository reservationRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.guestRepository = guestRepository;
        this.roomRepository = roomRepository;
        this.roomRateRepository = roomRateRepository;
        this.reservationRepository = reservationRepository;
        this.passwordEncoder = passwordEncoder;
    }
    @Override
    public void run(String... args) throws Exception {
        // Seed Guests
        Guest g1 = guestRepository.save(new Guest(null, "John", "Doe", "john@gmail.com", "555-0155", "ID-12345", "GOLD"));
        Guest g2 = guestRepository.save(new Guest(null, "Jane", "Smith", "jane@gmail.com", "555-0166", "ID-67890", "PLATINUM"));
        // Seed Users
        userRepository.save(new User(null, "guest", passwordEncoder.encode("guest123"), "GUEST", g1.getId()));
        userRepository.save(new User(null, "desk", passwordEncoder.encode("desk123"), "FRONT_DESK", null));
        userRepository.save(new User(null, "admin", passwordEncoder.encode("adminpwd123"), "ADMIN", null));
        // Seed Rooms
        Room r1 = roomRepository.save(new Room(null, "101", 1, "SINGLE", "AVAILABLE", "Wi-Fi, TV"));
        Room r2 = roomRepository.save(new Room(null, "202", 2, "DOUBLE", "AVAILABLE", "Wi-Fi, TV, Mini-bar"));
        Room r3 = roomRepository.save(new Room(null, "305", 3, "SUITE", "OCCUPIED", "Wi-Fi, TV, Jacuzzi"));
        // Seed Rates
        roomRateRepository.save(new RoomRate(null, "SINGLE", "SPRING", 99.0, LocalDate.now().minusMonths(1), LocalDate.now().plusMonths(3)));
        roomRateRepository.save(new RoomRate(null, "DOUBLE", "SPRING", 149.0, LocalDate.now().minusMonths(1), LocalDate.now().plusMonths(3)));
        roomRateRepository.save(new RoomRate(null, "SUITE", "SPRING", 299.0, LocalDate.now().minusMonths(1), LocalDate.now().plusMonths(3)));
        // Seed Reservations
        reservationRepository.save(new Reservation(null, g1.getId(), r3.getId(), LocalDate.now().minusDays(2), LocalDate.now().plusDays(2), "CONFIRMED", 598.0));
    }
}