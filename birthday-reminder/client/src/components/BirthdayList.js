import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Typography,
  Paper,
  Box,
} from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import axios from 'axios';

function BirthdayList() {
  const [birthdays, setBirthdays] = useState([]);

  useEffect(() => {
    fetchBirthdays();
  }, []);

  const fetchBirthdays = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/birthdays');
      setBirthdays(response.data);
    } catch (error) {
      console.error('Error fetching birthdays:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/api/birthdays/${id}`);
      fetchBirthdays();
    } catch (error) {
      console.error('Error deleting birthday:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Birthdays</Typography>
        <Button
          variant="contained"
          color="primary"
          component={Link}
          to="/add"
        >
          Add Birthday
        </Button>
      </Box>
      <Paper elevation={3}>
        <List>
          {birthdays.map((birthday) => (
            <ListItem key={birthday._id}>
              <ListItemText
                primary={birthday.name}
                secondary={`${format(new Date(birthday.date), 'MMMM d')}${
                  birthday.year ? `, ${birthday.year}` : ''
                }`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="edit"
                  component={Link}
                  to={`/edit/${birthday._id}`}
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleDelete(birthday._id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

export default BirthdayList; 