document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const eventForm = document.getElementById('event-form');
    const eventList = document.getElementById('event-list');
    const displayEventsBtn = document.getElementById('display-events-btn');

    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const name = document.getElementById('name').value;
            const surname = document.getElementById('surname').value;
            const age = document.getElementById('age').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return;
            }

            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, surname, age, email, password }),
            });

            const message = await response.text();
            alert(message);
            if (response.ok) {
                window.location.href = 'login.html';
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                window.location.href = 'main.html';
            } else {
                const message = await response.text();
                alert(message);
            }
        });
    }

    if (eventForm) {
        eventForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const name = document.getElementById('eventName').value;
            const date = document.getElementById('eventDate').value;
            const genre = document.getElementById('eventGenre').value;
            const price = document.getElementById('ticketPrice').value;
            const location = document.getElementById('eventLocation').value;

            const response = await fetch('/api/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, date, genre, price, location }),
            });

            const newEvent = await response.json();
             renderEvents([newEvent, ...Array.from(eventList.children)]);
        });

        async function fetchEvents() {
            const response = await fetch('/api/events');
            const events = await response.json();
            renderEvents(events);
        }

        function renderEvents(events) {
            eventList.innerHTML = '';
            events.forEach(event => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div>
                        <strong>${event.name}</strong> - ${event.date}<br>
                        Genre: ${event.genre}<br>
                        //Ticket Price: ${event.price}<br>
                       // Location: ${event.location}
                    </div>
                    <div>
                        <button onclick="editEvent('${event._id}')">Edit</button>
                        <button onclick="deleteEvent('${event._id}')">Delete</button>
                    </div>
                `;
                eventList.appendChild(li);
            });
        }

        window.deleteEvent = async (id) => {
            await fetch(`/api/events/${id}`, {
                method: 'DELETE',
            });
            fetchEvents();
        };

        window.editEvent = async (id) => {
            const name = prompt("Enter new event name");
            const date = prompt("Enter new event date (YYYY-MM-DD)");
            const genre = prompt("Enter new event genre");
            const price = prompt("Enter new ticket price");
            const location = prompt("Enter new event location");

            if (name && date && genre && price && location) {
                await fetch(`/api/events/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, date, genre, price, location }),
                });
                fetchEvents();
            }
        }; 

        fetchEvents();
    }

    if (displayEventsBtn) {
        displayEventsBtn.addEventListener('click', () => {
            window.location.href = 'events.html';
        });
    }
});