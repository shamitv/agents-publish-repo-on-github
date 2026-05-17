let selectedSeatId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadSeatMap();
});

function loadSeatMap() {
    const flightId = document.getElementById("flightId").value;
    
    fetch(`/api/flights/${flightId}/seats`)
        .then(res => res.json())
        .then(seats => {
            const grid = document.getElementById("seatGrid");
            grid.innerHTML = '';
            
            seats.forEach(seat => {
                const cell = document.createElement("div");
                
                // Base classes
                let seatClassString = 'seat-cell';
                
                if (!seat.isAvailable) {
                    seatClassString += ' taken';
                    cell.title = `Seat ${seat.seatNumber} (Reserved)`;
                } else {
                    seatClassString += ' available ' + seat.seatClass.toLowerCase();
                    cell.title = `Seat ${seat.seatNumber} (${seat.seatClass} Class) - Click to Select`;
                    
                    // Click handler
                    cell.onclick = () => selectSeat(seat.id, seat.seatNumber, seat.seatClass, cell);
                }
                
                cell.className = seatClassString;
                cell.innerText = seat.seatNumber;
                grid.appendChild(cell);
            });
        })
        .catch(err => {
            console.error("Error loading seat map:", err);
            alert("Error loading seat configuration.");
        });
}

function selectSeat(id, number, seatClass, cellElement) {
    // Unselect previous
    const active = document.querySelector(".seat-cell.selected");
    if (active) {
        active.classList.remove("selected");
    }
    
    // Select current
    cellElement.classList.add("selected");
    selectedSeatId = id;
    
    // Update Checkout Panel
    document.getElementById("selectedSeatLabel").innerText = number;
    document.getElementById("selectedSeatClassLabel").innerText = seatClass;
    document.getElementById("checkoutPanel").style.display = 'block';
}

function bookSelectedSeat() {
    if (!selectedSeatId) {
        alert("Please select a seat first.");
        return;
    }
    
    const flightId = document.getElementById("flightId").value;
    
    const payload = {
        flightId: parseInt(flightId),
        seatId: selectedSeatId
    };
    
    fetch('/api/bookings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            window.location.href = '/dashboard?bookingSuccess=true';
        } else {
            res.json().then(data => {
                alert("Booking failed: " + (data.status || "Unknown error"));
            });
        }
    })
    .catch(err => {
        console.error("Booking error:", err);
        alert("Error completing booking.");
    });
}
