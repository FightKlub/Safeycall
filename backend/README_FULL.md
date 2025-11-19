# 🛡️ SaferCall AI Backend

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Real-time scam detection system powered by AI and machine learning. SaferCall AI analyzes phone calls and text messages to identify potential scams, providing instant protection against fraud.

## 🌟 Features

- **🎤 Audio Scam Detection**: Upload audio recordings for real-time transcription and scam analysis
- **💬 Text Scam Detection**: Analyze text messages for scam indicators
- **🤖 AI-Powered Explanations**: Get detailed explanations of why content is flagged as a scam
- **☁️ AWS S3 Integration**: Secure cloud storage for audio files
- **📊 Advanced Pattern Matching**: Multi-layer detection using keywords and regex patterns
- **🔐 Enterprise Security**: Environment-based credential management and secure API access
- **📈 Comprehensive Logging**: Full request/response tracking and error monitoring

## 🏗️ Architecture

```
SaferCall AI Backend
│
├── Speech-to-Text (Whisper)
├── Scam Detection Engine
│   ├── Keyword Matching
│   ├── Pattern Recognition
│   └── Confidence Scoring
├── LLM Explainer (Google Gemini)
├── AWS S3 Storage
└── RESTful API (FastAPI)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for audio processing)
- AWS Account (for S3 storage)
- Google Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/safercall-ai.git
cd safercall-ai/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install FFmpeg**
```bash
# On Ubuntu/Debian
sudo apt-get install ffmpeg

# On macOS
brew install ffmpeg

# On Windows
# Download from https://ffmpeg.org/download.html
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Edit the `.env` file with your credentials:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET_NAME=your_bucket_name
SECRET_KEY=your_secret_key

# Optional
ENVIRONMENT=development
DEBUG_MODE=True
LOG_LEVEL=INFO
```

### Running the Application

**Development mode:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Root Endpoint
```http
GET /
```

### Scan Audio File
```http
POST /api/v1/scan_audio/
Content-Type: multipart/form-data

file: audio_file.mp3
store_in_s3: false
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00",
  "audio_metadata": {
    "filename": "call_recording.mp3",
    "file_size_mb": 2.5
  },
  "transcription": {
    "text": "Hello, this is regarding your bank account...",
    "length": 245
  },
  "scam_detection": {
    "is_scam": true,
    "scam_type": "financial_fraud",
    "confidence_score": 85,
    "severity": "high",
    "keywords_found": ["bank account", "otp", "verify"]
  },
  "analysis": {
    "explanation": "This call shows multiple red flags...",
    "recommendations": {...}
  }
}
```

### Scan Text Message
```http
POST /api/v1/scan_text/
Content-Type: application/x-www-form-urlencoded

text=Your account will be suspended. Click here to verify.
```

**Response:**
```json
{
  "success": true,
  "scam_detection": {
    "is_scam": true,
    "scam_type": "phishing",
    "confidence_score": 90,
    "severity": "high"
  },
  "analysis": {
    "explanation": "This message uses urgency tactics...",
    "recommendations": {...}
  }
}
```

## 🔧 Configuration Files

### Environment Variables (.env)
All sensitive credentials and configuration options.

### app/config.py
- Application settings
- Scam detection keywords
- Logging configuration
- Security settings

## 🗂️ Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
│
├── app/
│   ├── config.py        # Configuration management
│   ├── routes.py        # API endpoints
│   ├── models.py        # Data models
│   ├── scam_detector.py # Scam detection logic
│   ├── llm_explainer.py # AI explanation generation
│   ├── stt_module.py    # Speech-to-text processing
│   ├── s3_storage.py    # AWS S3 integration
│   └── utils.py         # Utility functions
│
└── logs/                # Application logs
```

## 🔐 Security Features

- ✅ Environment-based credential management
- ✅ Input validation and sanitization
- ✅ Rate limiting support
- ✅ CORS configuration
- ✅ Secure file upload handling
- ✅ AWS IAM role-based access
- ✅ Comprehensive error handling

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_scam_detector.py
```

## 📊 Monitoring & Logging

Logs are stored in the `logs/` directory:
- `safercall.log` - Main application log
- Automatic log rotation (10MB per file, 5 backups)
- Structured logging with timestamps and context

## 🚢 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### AWS Deployment
- Deploy on AWS Lambda with API Gateway
- Use AWS Elastic Beanstalk for scalability
- Configure AWS CloudWatch for monitoring

### Environment Setup
1. Set all required environment variables in your deployment platform
2. Ensure FFmpeg is installed in the runtime environment
3. Configure AWS IAM roles for S3 access
4. Set up SSL/TLS certificates for HTTPS

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech-to-text capabilities
- **Google Gemini** - AI-powered scam explanations
- **FastAPI** - Modern web framework
- **AWS** - Cloud infrastructure

## 📞 Support

For support and questions:
- 📧 Email: support@safercall.ai
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/safercall-ai/issues)
- 📖 Documentation: [Full Docs](https://docs.safercall.ai)

## 🔄 Version History

- **v1.0.0** (2024-01) - Initial release
  - Audio and text scam detection
  - AWS S3 integration
  - AI-powered explanations
  - Comprehensive API documentation

---

**Built with ❤️ for a safer digital world**
