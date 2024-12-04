
let currentRotation = 0; // Tracks the total rotation of the wheel
const tableNumbers = ["1", "2", "3", "4", "5", "6", "7"];
const segmentCount = tableNumbers.length;
const anglePerSegment = 360 / segmentCount; // Each segment's angle in degrees

// Define goToWheel globally for the index page
function goToWheel() {
    const dropdown = document.getElementById("nameDropdown");
    const selectedName = dropdown.value;
    if (selectedName) {
        localStorage.setItem("selectedEmployee", selectedName);
        window.location.href = "/wheel";
    } else {
        alert("Please select your name!");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const spinButton = document.getElementById("spinButton");
    const returnButton = document.getElementById("returnButton");

    if (spinButton) spinButton.addEventListener("click", spinWheel);
    if (returnButton) returnButton.addEventListener("click", returnToSearch);

    if (document.getElementById("wheelCanvas")) {
        drawWheel();
    }
});

function drawWheel() {
    const canvas = document.getElementById("wheelCanvas");
    const ctx = canvas.getContext("2d");
    const radius = canvas.width / 2;

    // Loop through each segment
    for (let i = 0; i < segmentCount; i++) {
        const startAngle = i * anglePerSegment * (Math.PI / 180);
        const endAngle = startAngle + anglePerSegment * (Math.PI / 180);

        // Create gradient for each segment
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, getGradientColor(i).start);
        gradient.addColorStop(1, getGradientColor(i).end);

        // Draw the segment with border
        ctx.beginPath();
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius, startAngle, endAngle);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "gold";
        ctx.stroke();

        // Add shadow for 3D effect
        ctx.shadowColor = "rgba(0, 0, 0, 0.3)";
        ctx.shadowBlur = 10;

        // Add table numbers
        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(startAngle + anglePerSegment * (Math.PI / 360));
        ctx.textAlign = "center";
        ctx.fillStyle = "#fff";
        ctx.font = "bold 20px Georgia"; // Elegant font
        ctx.fillText(tableNumbers[i], radius * 0.7, 10);
        ctx.restore();
    }
}

// Gradient colors for each segment
function getGradientColor(index) {
    const gradients = [
        { start: "#FF9A8B", end: "#FF6A88" },
        { start: "#FFB199", end: "#FF3C98" },
        { start: "#FFD700", end: "#FFC700" },
        { start: "#C6FFDD", end: "#FBD786" },
        { start: "#FC466B", end: "#3F5EFB" },
        { start: "#43C6AC", end: "#191654" },
        { start: "#3A1C71", end: "#D76D77" }
    ];
    return gradients[index % gradients.length];
}




function spinWheel() {
    const spinButton = document.getElementById("spinButton");
    spinButton.style.display = "none"; // Hide the button after click

    // Fetch available tables before spinning
    fetch("/available_tables")
        .then(response => response.json())
        .then(data => {
            const availableTables = data.available_tables;

            if (availableTables.length === 0) {
                alert("All tables are full!");
                spinButton.style.display = "block"; // Show the button again if no tables available
                return;
            }

            const segmentCount = availableTables.length;
            const anglePerSegment = 360 / segmentCount;
            const randomSpin = Math.floor(Math.random() * 360) + 1080; // At least 3 full spins plus random offset
            currentRotation += randomSpin;

            const canvas = document.getElementById("wheelCanvas");
            canvas.style.transition = "transform 3s ease-out";
            canvas.style.transform = `rotate(${currentRotation}deg)`;

            // Wait for the spin animation to complete
            setTimeout(() => {
                const normalizedRotation = currentRotation % 360; // Normalize to 0-360 degrees
                const pointerAngle = (360 - normalizedRotation) % 360; // Pointer at 0 degrees
                const selectedIndex = Math.floor(pointerAngle / anglePerSegment) % segmentCount;

                const selectedTable = availableTables[selectedIndex];

                // Add glow effect to pointer
                const pointer = document.getElementById("pointer");
                pointer.innerText = `Table ${selectedTable}`;
                pointer.classList.add("glow");
                setTimeout(() => pointer.classList.remove("glow"), 10000);

                // Retrieve the attendee's name from localStorage
                const attendeeName = localStorage.getItem("selectedEmployee") || "Guest";

                // Update the message below the wheel
                const message = document.getElementById("message");
                message.innerHTML = `🎉 Welcome <br>
                                    <strong>${attendeeName}</strong>! <br>
                                    You are assigned to <strong>Table ${selectedTable}</strong>! 🎉`;

                // Add glow effect to message
                message.classList.add("glow");
                setTimeout(() => message.classList.remove("glow"), 10000);

                // Prevent duplicate draws and update the Excel sheet
                updateAssignment(attendeeName, selectedTable);

                spinButton.style.display = "none"; // Hide the button after spin completion
				
				// Redirect to the main page after 10 seconds
                setTimeout(() => {
                    window.location.href = "/";
                }, 9000);
            }, 3000);
        })
        .catch(err => {
            console.error("Error fetching available tables:", err);
            spinButton.style.display = "block"; // Show the button again in case of error
        });
}





// Function to update assignment and prevent duplicates
function updateAssignment(name, table) {
    fetch("/update_assignment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, table: table })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`${name} assigned to Table ${table}`);
            } else {
                console.error(data.error);
            }
        })
        .catch(error => console.error("Error updating assignment:", error));
}


function returnToSearch() {
    window.location.href = "/";
}

function getColor(index) {
    const colors = ["#FF5733", "#FFC300", "#DAF7A6", "#33FF57", "#33D4FF", "#A633FF", "#FF33A1"];
    return colors[index % colors.length];
}

// Function to update assignment and prevent duplicates
function updateAssignment(name, table) {
    fetch("/update_assignment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, table: table })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`${name} assigned to Table ${table}`);
            } else {
                console.error(data.error);
            }
        })
        .catch(error => console.error("Error updating assignment:", error));
}

// Update Wheel Segments Dynamically Based on Availability
function updateWheelSegments() {
    fetch("/view_assignments") // Fetch table status
        .then(response => response.json())
        .then(data => {
            const tableStatus = data.table_status;
            const availableTables = Object.keys(tableStatus)
                .filter(table => tableStatus[table] < 10)
                .map(table => parseInt(table)); // Get tables with <10 assigned

            if (availableTables.length === 0) {
                alert("All tables are full!");
                return;
            }

            // Redraw the wheel with available tables only
            tableNumbers = availableTables; // Update global tableNumbers
            drawWheel();
        })
        .catch(error => console.error("Error fetching table status:", error));
}

// Call this function to redraw the wheel before spinning
document.addEventListener("DOMContentLoaded", function () {
    updateWheelSegments(); // Ensure wheel updates dynamically
    const spinButton = document.getElementById("spinButton");
    spinButton.addEventListener("click", spinWheel);

});
