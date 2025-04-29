const express = require('express');
const router = express.Router();
const Birthday = require('../models/Birthday');

// Get all birthdays for a user
router.get('/', async (req, res) => {
  try {
    const birthdays = await Birthday.find({ userId: req.user.id });
    res.json(birthdays);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Add a new birthday
router.post('/', async (req, res) => {
  const birthday = new Birthday({
    name: req.body.name,
    date: req.body.date,
    year: req.body.year,
    userId: req.user.id,
    source: 'manual'
  });

  try {
    const newBirthday = await birthday.save();
    res.status(201).json(newBirthday);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Update a birthday
router.patch('/:id', async (req, res) => {
  try {
    const birthday = await Birthday.findById(req.params.id);
    if (!birthday) return res.status(404).json({ message: 'Birthday not found' });
    
    if (req.body.name) birthday.name = req.body.name;
    if (req.body.date) birthday.date = req.body.date;
    if (req.body.year) birthday.year = req.body.year;
    
    const updatedBirthday = await birthday.save();
    res.json(updatedBirthday);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Delete a birthday
router.delete('/:id', async (req, res) => {
  try {
    const birthday = await Birthday.findById(req.params.id);
    if (!birthday) return res.status(404).json({ message: 'Birthday not found' });
    
    await birthday.remove();
    res.json({ message: 'Birthday deleted' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router; 