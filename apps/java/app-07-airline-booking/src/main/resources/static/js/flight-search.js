function performFlightSearch(e) {
    e.preventDefault();

    const origin = document.getElementById("searchOrigin").value.trim();
    const destination = document.getElementById("searchDestination").value.trim();
    const date = document.getElementById("searchDate").value.trim();

    const url = `/api/flights/search?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&date=${encodeURIComponent(date)}`;

    fetch(url)
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to search flights");
            }
            return res.json();
        })
        .then(flights => {
            const resultsSection = document.getElementById("searchResultsSection");
            const resultsList = document.getElementById("searchResultsList");
            
            resultsList.innerHTML = '';
            
            if (flights.length === 0) {
                resultsList.innerHTML = `
                    <div style="text-align: center; color: var(--text-muted); padding: 16px;">
                        No flights found matching criteria.
                    </div>
                `;
                resultsSection.style.display = 'block';
                return;
            }

            flights.forEach(flight => {
                const card = document.createElement("div");
                card.className = "glass-card";
                card.style.padding = "20px";
                card.style.border = "1px solid var(--glass-border)";
                card.style.display = "flex";
                card.style.justifyContent = "space-between";
                card.style.alignItems = "center";

                card.innerHTML = `
                    <div>
                        <div style="font-size: 16px; font-weight: 700; color: var(--primary);">${flight.airline} — ${flight.flightNumber}</div>
                        <div style="font-size: 14px; margin-top: 8px; color: var(--text-color);">
                            ${flight.origin} ➔ ${flight.destination}
                        </div>
                        <div style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">
                            Dep: ${flight.departureTime} | Arr: ${flight.arrivalTime}
                        </div>
                        <div style="font-size: 13px; color: var(--success); margin-top: 4px; font-weight: 600;">
                            ${flight.availableSeats} seats left
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 12px;">$${flight.price.toFixed(2)}</div>
                        <a href="/flights/${flight.id}/seats" class="btn" style="padding: 8px 16px; font-size: 13px; border-radius: 6px;">Select Seat</a>
                    </div>
                `;
                resultsList.appendChild(card);
            });

            resultsSection.style.display = 'block';
        })
        .catch(err => {
            console.error(err);
            alert("Error finding flights.");
        });
}
