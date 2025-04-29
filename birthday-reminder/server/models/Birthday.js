const mongoose = require('mongoose');

const birthdaySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  date: {
    type: Date,
    required: true
  },
  year: {
    type: Number,
    required: false
  },
  userId: {
    type: String,
    required: true
  },
  source: {
    type: String,
    enum: ['manual', 'facebook'],
    default: 'manual'
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Birthday', birthdaySchema); 