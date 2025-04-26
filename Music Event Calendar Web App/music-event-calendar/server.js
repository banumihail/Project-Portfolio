const express = require('express');
const path = require('path');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/musicEventCalendar', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log('MongoDB connected...');
}).catch(err => console.log(err));

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// User schema and model
const userSchema = new mongoose.Schema({
    name: String,
    surname: String,
    age: Number,
    email: String,
    password: String
});

const eventSchema = new mongoose.Schema({
    name: String,
    date: String,
    genre: String,
    price: String,
    location: String
});

const User = mongoose.model('User', userSchema);
const Event = mongoose.model('Event', eventSchema);

// Routes
app.post('/api/signup', async (req, res) => {
    const { name, surname, age, email, password } = req.body;
    const newUser = new User({ name, surname, age, email, password });
    await newUser.save();
    res.send('User registered successfully');
});

app.post('/api/login', async (req, res) => {
    const { email, password } = req.body;
    const user = await User.findOne({ email, password });
    if (user) {
        res.send('Login successful');
    } else {
        res.status(401).send('Invalid email or password');
    }
});

app.post('/api/events', async (req, res) => {
    const { name, date, genre, price, location } = req.body;
    const newEvent = new Event({ name, date, genre, price, location });
    await newEvent.save();
    res.json(newEvent);
});

app.get('/api/events', async (req, res) => {
    const events = await Event.find();
    res.json(events);
});

app.put('/api/events/:id', async (req, res) => {
    const { id } = req.params;
    const { name, date, genre, price, location } = req.body;
    const updatedEvent = await Event.findByIdAndUpdate(id, { name, date, genre, price, location }, { new: true });
    res.json(updatedEvent);
});

app.delete('/api/events/:id', async (req, res) => {
    const { id } = req.params;
    await Event.findByIdAndDelete(id);
    res.send('Event deleted');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});