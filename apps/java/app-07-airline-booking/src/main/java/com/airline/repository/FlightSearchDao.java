package com.airline.repository;

import com.airline.model.Flight;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

@Repository
public class FlightSearchDao {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<Flight> searchFlights(String origin, String destination, String date) {
        // VULNERABILITY A03: Flight search SQL is built by concatenating user-supplied parameters.
        String sql = "SELECT * FROM flights WHERE origin = '" + origin
                   + "' AND destination = '" + destination
                   + "' AND CAST(departure_time AS DATE) = '" + date + "'";
        return jdbcTemplate.query(sql, new FlightRowMapper());
    }

    private static class FlightRowMapper implements RowMapper<Flight> {
        @Override
        public Flight mapRow(ResultSet rs, int rowNum) throws SQLException {
            return Flight.builder()
                    .id(rs.getLong("id"))
                    .flightNumber(rs.getString("flight_number"))
                    .airline(rs.getString("airline"))
                    .origin(rs.getString("origin"))
                    .destination(rs.getString("destination"))
                    .departureTime(rs.getTimestamp("departure_time").toLocalDateTime())
                    .arrivalTime(rs.getTimestamp("arrival_time").toLocalDateTime())
                    .price(rs.getBigDecimal("price"))
                    .totalSeats(rs.getInt("total_seats"))
                    .availableSeats(rs.getInt("available_seats"))
                    .build();
        }
    }
}
