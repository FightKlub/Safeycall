# SaferCall AI Backend - Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup Guide](#setup-guide)
4. [API Documentation](#api-documentation)
5. [Deployment](#deployment)
6. [Security](#security)
7. [Troubleshooting](#troubleshooting)

## Project Overview

SaferCall AI is a comprehensive scam detection system that analyzes audio recordings and text messages to identify potential fraud attempts. The system leverages advanced AI technologies including:

- **OpenAI Whisper**: For accurate speech-to-text transcription
- **Google Gemini API**: For intelligent scam explanation generation
- **AWS S3**: For secure audio file storage
- **FastAPI**: For high-performance REST API

### Key Features
- Real-time audio transcription and analysis
- Text message scam detection
- AI-powered explanations
- Cloud storage integration
- Comprehensive logging and monitoring

## Architecture

### System Components

```
┌─────────────────┐
│  Client Apps    │
│ (Flutter/Web)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│Whisper │ │ Gemini │
│  STT   │ │  API   │
└────────┘ └────────┘
    │
    ▼
┌────────┐
│AWS S3  │
│Storage │
└────────┘
```

### Data Flow

1. **Audio Upload**: Client uploads audio file via multipart/form-data
2. **Transcription**: Whisper processes audio to text
3. **Detection**: Pattern matching and keyword analysis
4. **AI Analysis**: Gemini generates detailed explanation
5. **Storage**: Optional S3 storage for scam recordings
6. **Response**: Comprehensive JSON response to client

## Setup Guide

### Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] FFmpeg installed
- [ ] AWS account created
- [ ] S3 bucket created
- [ ] Google Cloud account with Gemini API access
- [ ] API keys generated

### Step-by-Step Installation

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/yourusername/safercall-ai.git
cd safercall-ai/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables
Create `.env` file:
```env
GEMINI_API_KEY=AIzaSyDFEN1_HHBvLlZTXyBKd-tiXSM3p1BUvck
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=safercall-audio-storage
SECRET_KEY=your-secret-key-here
```

#### 4. Run Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Endpoint: Scan Audio
**POST** `/api/v1/scan_audio/`

Analyzes audio file for scam indicators.

**Request:**
```http
POST /api/v1/scan_audio/
Content-Type: multipart/form-data

file: [audio file]
store_in_s3: false
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00",
  "scam_detection": {
    "is_scam": true,
    "confidence_score": 85,
    "severity": "high"
  }
}
```

### Endpoint: Scan Text
**POST** `/api/v1/scan_text/`

Analyzes text message for scam indicators.

**Request:**
```http
POST /api/v1/scan_text/
Content-Type: application/x-www-form-urlencoded

text=Your account will be suspended
```

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t safercall-backend .

# Run container
docker run -p 8000:8000 --env-file .env safercall-backend
```

### Docker Compose
```bash
docker-compose up -d
```

### AWS Elastic Beanstalk
1. Install EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Deploy: `eb deploy`

## Security

### Best Practices Implemented
- ✅ Environment variable-based configuration
- ✅ No hardcoded credentials in source code
- ✅ Input validation and sanitization
- ✅ Rate limiting capability
- ✅ CORS properly configured
- ✅ File upload size restrictions
- ✅ Secure error handling

### AWS IAM Policy (Recommended)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::safercall-audio-storage/*"
    }
  ]
}
```

## Troubleshooting

### Common Issues

**Issue: Whisper model loading fails**
```bash
# Solution: Ensure FFmpeg is installed
# Windows: Download from ffmpeg.org
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

**Issue: AWS credentials not found**
```bash
# Solution: Verify .env file exists and has correct values
# Check AWS credentials: aws sts get-caller-identity
```

**Issue: Import errors**
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Logs Location
- Application logs: `logs/safercall.log`
- Error logs: `logs/safercall.log` (filtered by level)

### Support Contacts
- Technical Support: support@safercall.ai
- GitHub Issues: https://github.com/yourusername/safercall-ai/issues

---

**Last Updated**: January 2024  
**Version**: 1.0.0
