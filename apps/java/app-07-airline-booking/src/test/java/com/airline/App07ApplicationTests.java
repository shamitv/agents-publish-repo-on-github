package com.airline;

import com.airline.dto.SeatHoldRequest;
import com.airline.model.Booking;
import com.airline.model.Flight;
import com.airline.model.Passenger;
import com.airline.model.Seat;
import com.airline.model.SeatHold;
import com.airline.repository.BookingRepository;
import com.airline.repository.FlightRepository;
import com.airline.repository.PassengerRepository;
import com.airline.repository.SeatHoldRepository;
import com.airline.repository.SeatRepository;
import com.airline.service.PnrGenerator;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class App07ApplicationTests {

    @Autowired
    private PassengerRepository passengerRepository;

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private SeatRepository seatRepository;

    @Autowired
    private SeatHoldRepository seatHoldRepository;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private PnrGenerator pnrGenerator;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void contextLoads() {
    }

    @Test
    void testPnrGenerationLengthAndAlphanumeric() {
        String pnr = pnrGenerator.generate();
        assertNotNull(pnr);
        assertEquals(8, pnr.length());
        assertTrue(pnr.matches("[A-Z0-9]{8}"));
    }

    @Test
    void testPassengerRegistrationHashingDecoy() {
        Passenger passenger = Passenger.builder()
                .email("test-john@gmail.com")
                .passwordHash(passwordEncoder.encode("testpass123"))
                .firstName("TestJohn")
                .lastName("Doe")
                .role("PASSENGER")
                .build();
        
        Passenger saved = passengerRepository.save(passenger);
        
        assertNotNull(saved.getId());
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("testpass123", saved.getPasswordHash()));
    }

    @Test
    void seatHoldReferencesArePredictableThroughApi() throws Exception {
        List<Seat> seats = availableSeatsOnSameFlight(2);
        String firstHoldRef = createHold("john@gmail.com", seats.get(0));
        String secondHoldRef = createHold("john@gmail.com", seats.get(1));

        assertTrue(firstHoldRef.matches("HOLD\\d{6}"));
        assertTrue(secondHoldRef.matches("HOLD\\d{6}"));
        int firstNumber = Integer.parseInt(firstHoldRef.substring(4));
        int secondNumber = Integer.parseInt(secondHoldRef.substring(4));
        assertEquals(firstNumber + 1, secondNumber);
    }

    @Test
    void differentPassengerCanReadAndModifyHoldButSafeEndpointRejects() throws Exception {
        List<Seat> seats = availableSeatsOnSameFlight(2);
        Seat originalSeat = seats.get(0);
        Seat replacementSeat = seats.get(1);
        String holdRef = createHold("john@gmail.com", originalSeat);

        mockMvc.perform(get("/api/holds/{holdRef}", holdRef)
                        .with(user("jane@gmail.com").roles("PASSENGER")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.passengerEmail").value("john@gmail.com"))
                .andExpect(jsonPath("$.seatId").value(originalSeat.getId().intValue()));

        mockMvc.perform(get("/api/holds/owned/{holdRef}", holdRef)
                        .with(user("jane@gmail.com").roles("PASSENGER")))
                .andExpect(status().isForbidden());

        mockMvc.perform(put("/api/holds/{holdRef}/seat", holdRef)
                        .with(user("jane@gmail.com").roles("PASSENGER"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"seatId\":" + replacementSeat.getId() + "}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.seatId").value(replacementSeat.getId().intValue()));
    }

    @Test
    void differentPassengerCanConfirmVictimHoldAsOwnBooking() throws Exception {
        Seat heldSeat = availableSeatsOnSameFlight(1).get(0);
        String holdRef = createHold("john@gmail.com", heldSeat);

        String body = mockMvc.perform(post("/api/holds/{holdRef}/confirm", holdRef)
                        .with(user("jane@gmail.com").roles("PASSENGER")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CONFIRMED_FROM_HOLD"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        String pnr = objectMapper.readTree(body).get("pnr").asText();
        Booking booking = bookingRepository.findByPnr(pnr).orElseThrow();
        assertEquals("jane@gmail.com", booking.getPassenger().getEmail());
        assertEquals(heldSeat.getId(), booking.getSeat().getId());

        SeatHold hold = seatHoldRepository.findByHoldRef(holdRef).orElseThrow();
        assertEquals("john@gmail.com", hold.getPassenger().getEmail());
        assertEquals("CONFIRMED", hold.getStatus());
    }

    private String createHold(String username, Seat seat) throws Exception {
        SeatHoldRequest request = new SeatHoldRequest();
        request.setFlightId(seat.getFlight().getId());
        request.setSeatId(seat.getId());

        String body = mockMvc.perform(post("/api/holds")
                        .with(user(username).roles("PASSENGER"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        JsonNode json = objectMapper.readTree(body);
        return json.get("holdRef").asText();
    }

    private List<Seat> availableSeatsOnSameFlight(int count) {
        for (Flight flight : flightRepository.findAll()) {
            List<Seat> seats = seatRepository.findByFlightIdAndIsAvailable(flight.getId(), true);
            if (seats.size() >= count) {
                return seats.subList(0, count);
            }
        }
        throw new IllegalStateException("Not enough available seats for test");
    }
}
