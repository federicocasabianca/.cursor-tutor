import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import axios from 'axios';

function BirthdayForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [formData, setFormData] = useState({
    name: '',
    date: new Date(),
    year: '',
  });

  useEffect(() => {
    if (id) {
      fetchBirthday();
    }
  }, [id]);

  const fetchBirthday = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/birthdays/${id}`);
      const birthday = response.data;
      setFormData({
        name: birthday.name,
        date: new Date(birthday.date),
        year: birthday.year || '',
      });
    } catch (error) {
      console.error('Error fetching birthday:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (id) {
        await axios.patch(`http://localhost:5000/api/birthdays/${id}`, formData);
      } else {
        await axios.post('http://localhost:5000/api/birthdays', formData);
      }
      navigate('/');
    } catch (error) {
      console.error('Error saving birthday:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {id ? 'Edit Birthday' : 'Add Birthday'}
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            margin="normal"
          />
          <DatePicker
            label="Birth Date"
            value={formData.date}
            onChange={(newValue) => {
              setFormData((prev) => ({ ...prev, date: newValue }));
            }}
            renderInput={(params) => (
              <TextField {...params} fullWidth margin="normal" required />
            )}
          />
          <TextField
            fullWidth
            label="Birth Year (Optional)"
            name="year"
            type="number"
            value={formData.year}
            onChange={handleChange}
            margin="normal"
          />
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              type="submit"
            >
              {id ? 'Update' : 'Add'}
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      </Paper>
    </LocalizationProvider>
  );
}

export default BirthdayForm; 