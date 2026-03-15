# AQI Voice Assistant - AI-Powered Air Quality & Lung Health Prediction System

A production-ready AI Voice Assistant system for Air Quality Index (AQI) prediction and Lung Health Risk Assessment. Built with FastAPI backend and React + Tailwind + Framer Motion frontend.

![AQI Assistant](https://img.shields.io/badge/Version-1.0.0-blue)
![React](https://img.shields.io/badge/React-18.2-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## 🚀 Features

### Backend (FastAPI)
- **REST API** with prediction endpoints (`/predict/aqi`, `/predict/lung-health`, `/health`, `/model-info`)
- **JWT Authentication** for secure API access
- **Rate Limiting** to prevent abuse
- **Async Processing** for better performance
- **Caching** support for faster responses
- **Logging** and error handling
- **Docker Support** for easy deployment
- **Model Optimization** for fast inference

### Frontend (React + Tailwind)
- **Voice Assistant** with real-time audio visualization
- **AQI Dashboard** with interactive gauge
- **Lung Health Risk** assessment with recommendations
- **Analytics Charts** (Recharts) for historical data and forecasts
- **File Upload** support for batch predictions
- **Smooth Animations** using Framer Motion
- **Modern Glass UI** design
- **Responsive Design** for all devices

## 📁 Project Structure

```
aqi_assistant/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env               # Environment configuration
│   ├── Dockerfile         # Docker configuration
│   └── models/            # ML model files
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Tailwind styles
│   ├── package.json       # Node dependencies
│   ├── tailwind.config.js # Tailwind config
│   ├── vite.config.js    # Vite config
│   └── index.html        # HTML template
│
└── README.md             # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```
bash
cd aqi_assistant/backend
```

2. Create virtual environment:
```
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
bash
pip install -r requirements.txt
```

4. Configure environment:
```
bash
cp .env.example .env
# Edit .env with your API keys and settings
```

5. Run the server:
```
bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Frontend Setup

1. Navigate to frontend directory:
```
bash
cd aqi_assistant/frontend
```

2. Install dependencies:
```
bash
npm install
```

3. Configure API URL (optional):
```
bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

4. Run development server:
```
bash
npm run dev
```

5. Build for production:
```
bash
npm run build
```

The frontend will be available at `http://localhost:3000`

### Docker Deployment

```
bash
# Build and run with Docker Compose
docker-compose up -d

# Or manually
docker build -t aqi-assistant-backend ./backend
docker run -p 8000:8000 aqi-assistant-backend
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/model-info` | GET | Model information |
| `/predict/aqi` | POST | Predict AQI |
| `/predict/lung-health` | POST | Predict lung health risk |
| `/voice/command` | POST | Process voice command |
| `/predict/batch` | POST | Batch predictions |
| `/predict/audio` | POST | Audio file processing |

### Example Request

```
bash
# AQI Prediction
curl -X POST "http://localhost:8000/predict/aqi" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "pm25": 45,
    "pm10": 80,
    "temperature": 28,
    "humidity": 65
  }'
```

## 🎨 UI Features

### Dashboard
- Real-time AQI display with color-coded gauge
- Lung health risk assessment
- Pollutant level breakdown
- Weather information

### Voice Assistant
- Click-to-speak interface
- Audio wave visualization
- Real-time transcription
- AI-powered responses

### Analytics
- 24-hour AQI trend chart
- Pollutant comparison bar chart
- 5-day forecast line chart

## 🔧 Configuration

### Environment Variables (Backend)

```
env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Model
MODEL_PATH=./models
```

### Environment Variables (Frontend)

```
env
VITE_API_URL=http://localhost:8000
```

## 🚢 Deployment

### Vercel (Frontend)
```
bash
npm run build
vercel deploy
```

### Render/Railway (Backend)
```
bash
# Connect your GitHub repository
# Set environment variables
# Deploy automatically
```

### AWS EC2
```
bash
# SSH into instance
# Install Docker
# Run container
docker run -d -p 8000:8000 --name aqi-api your-image
```

## 🔐 Security

- JWT-based authentication
- Rate limiting (100 requests/minute)
- Input validation with Pydantic
- CORS configuration
- Secure headers

## 📊 Monitoring

- Health check endpoint
- Request logging
- Error tracking
- Performance metrics

## 🧪 Testing

```
bash
# Backend tests
pytest test_main.py -v

# Frontend tests
npm run test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - feel free to use this project for any purpose.

## 👨‍💻 Author

AQI Voice Assistant - AI-Powered Lung Health Prediction System

---

Built with ❤️ using FastAPI, React, Tailwind CSS, and Framer Motion
