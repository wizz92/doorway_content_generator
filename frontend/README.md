# React Frontend

Modern React frontend built with TypeScript, Material UI, and React Router.

## Features

- ✅ Material UI design system
- ✅ User authentication (login/logout)
- ✅ Protected routes
- ✅ Real-time job progress tracking
- ✅ File upload with drag-and-drop
- ✅ Error handling with toast notifications
- ✅ Responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API URL in `.env`:
```
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
├── components/      # Reusable components
│   ├── Auth/       # Authentication components
│   ├── Jobs/       # Job management components
│   ├── Layout/     # Layout components
│   └── Common/     # Common UI components
├── context/        # React contexts (Auth, Error)
├── pages/          # Page components
├── services/       # API service layer
└── App.tsx         # Main app component
```

## Usage

1. Start the backend server (port 8000)
2. Create a user: `python create_user.py username password`
3. Start the frontend: `npm run dev`
4. Login at http://localhost:5173/login
5. Upload CSV and create jobs
