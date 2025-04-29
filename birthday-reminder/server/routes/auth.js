const express = require('express');
const router = express.Router();
const passport = require('passport');
const Birthday = require('../models/Birthday');

// Facebook login route
router.get('/facebook',
  passport.authenticate('facebook', { scope: ['user_birthday'] })
);

// Facebook callback route
router.get('/facebook/callback',
  passport.authenticate('facebook', { failureRedirect: '/login' }),
  async (req, res) => {
    try {
      // Extract birthday from Facebook profile
      const birthday = req.user.birthday;
      if (birthday) {
        const [month, day, year] = birthday.split('/');
        const date = new Date(year, month - 1, day);
        
        // Save birthday to database
        const newBirthday = new Birthday({
          name: req.user.name,
          date: date,
          year: year,
          userId: req.user.id,
          source: 'facebook'
        });
        
        await newBirthday.save();
      }
      
      res.redirect('/');
    } catch (err) {
      console.error('Error saving Facebook birthday:', err);
      res.redirect('/');
    }
  }
);

module.exports = router; 