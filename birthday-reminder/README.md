# Birthday Reminder Application

A web application that helps you keep track of birthdays for your family members, friends, and acquaintances. The application allows you to import birthdays from Facebook and manually add new birthdays.

## Features

- Import birthdays from Facebook
- Manually add birthdays with optional year
- Edit and delete existing birthdays
- Modern and responsive UI
- Secure authentication

## Prerequisites

- Node.js (v14 or higher)
- MongoDB
- Facebook Developer Account

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd birthday-reminder
```

2. Install dependencies:
```bash
npm run install-all
```

3. Create a `.env` file in the server directory with the following variables:
```
MONGODB_URI=mongodb://localhost:27017/birthday-reminder
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

4. Create a `.env` file in the client directory with the following variable:
```
REACT_APP_FACEBOOK_APP_ID=your_facebook_app_id
```

5. Start the application:
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Facebook Integration

To enable Facebook integration:

1. Create a Facebook Developer account at https://developers.facebook.com
2. Create a new app
3. Add the Facebook Login product to your app
4. Configure the OAuth redirect URI to: http://localhost:5000/auth/facebook/callback
5. Copy the App ID and App Secret to your environment variables

## Usage

1. Log in using your Facebook account
2. Your Facebook friends' birthdays will be automatically imported
3. Add additional birthdays manually using the "Add Birthday" button
4. Edit or delete birthdays as needed

## Technologies Used

- Frontend:
  - React
  - Material-UI
  - React Router
  - Axios
  - date-fns

- Backend:
  - Node.js
  - Express
  - MongoDB
  - Passport.js
  - Facebook OAuth

## License

MIT 