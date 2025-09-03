# Israeli Law Chatbot Frontend

A professional React-based chat interface for an Israeli legal consultation AI assistant.

## Features

- **Professional Design**: Clean, responsive interface with Hebrew RTL support
- **Real-time Chat**: Interactive chat interface with typing indicators
- **API Integration**: Connects to FastAPI backend with axios
- **Responsive Layout**: Works on desktop and mobile devices
- **Error Handling**: Graceful error handling with user-friendly messages
- **Accessibility**: Professional styling with proper contrast and spacing

## Tech Stack

- **React 18** - Frontend framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **date-fns** - Date formatting and manipulation

## Getting Started

### Prerequisites

- Node.js 20.19+ or 22.12+
- npm

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd poc/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser

### Backend Configuration

Make sure your FastAPI backend is running on `http://localhost:8000` or update the `API_BASE_URL` in `src/App.jsx`.

## Project Structure

```
src/
├── components/
│   ├── ChatMessage.jsx      # Individual chat message component
│   ├── MessageInput.jsx     # Message input with send button
│   └── TypingIndicator.jsx  # "Typing..." indicator component
├── App.jsx                  # Main application component
├── index.css                # Global styles with Tailwind imports
└── main.jsx                 # React app entry point
```

## API Integration

The frontend communicates with the FastAPI backend via:

- **Endpoint**: `POST /api/v1/chat`
- **Request Format**:
  ```json
  {
    "user_prompt": "string",
    "chat_id": "string",
    "max_tokens": 1000,
    "temperature": 0.7
  }
  ```
- **Response Format**:
  ```json
  {
    "answer": "string",
    "chat_id": "string",
    "timestamp": "datetime",
    "processing_time_seconds": 0.0
  }
  ```

## Customization

### Colors

The app uses a custom color scheme defined in `tailwind.config.js`:
- **Primary**: Blue tones for buttons and accents
- **Secondary**: Gray tones for text and backgrounds

### Language

The interface is primarily in Hebrew with RTL support. English text is used for technical elements.

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Development

- The app includes hot reloading during development
- Tailwind classes are purged in production builds
- All components are responsive and mobile-friendly