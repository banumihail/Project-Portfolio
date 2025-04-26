const express = require('express');
const router = express.Router();
const Event = require('../models/Event');

// Create an event
router.post('/', async (req, res) => {
  const event = new Event(req.body);
  try {
    await event.save();
    res.status(201).send(event);
  } catch (e) {
    res.status(400).send(e);
  }
});

// Get all events
router.get('/', async (req, res) => {
  try {
    const events = await Event.find();
    res.status(200).send(events);
  } catch (e) {
    res.status(500).send(e);
  }
});

module.exports = router;
