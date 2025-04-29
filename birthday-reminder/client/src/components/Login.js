import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Button,
  Paper,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import FacebookLogin from 'react-facebook-login';

function Login() {
  const navigate = useNavigate();

  const responseFacebook = (response) => {
    if (response.accessToken) {
      // Store the access token in localStorage or state management
      localStorage.setItem('facebookToken', response.accessToken);
      navigate('/');
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom align="center">
        Login to Birthday Reminder
      </Typography>
      <Box sx={{ mt: 3 }}>
        <FacebookLogin
          appId={process.env.REACT_APP_FACEBOOK_APP_ID}
          autoLoad={false}
          fields="name,email,birthday"
          scope="public_profile,user_birthday"
          callback={responseFacebook}
          cssClass="facebook-login-button"
          icon="fa-facebook"
          textButton="Login with Facebook"
        />
      </Box>
      <Divider sx={{ my: 3 }} />
      <Typography variant="body2" color="text.secondary" align="center">
        By logging in, you agree to our Terms of Service and Privacy Policy
      </Typography>
    </Paper>
  );
}

export default Login; 