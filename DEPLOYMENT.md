# SaferCall AI - Deployment Guide

## Deployment Options

### 1. Local Development
```bash
uvicorn main:app --reload --port 8000
```

### 2. Production Server (Gunicorn + Uvicorn)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Docker Deployment

#### Build and Run
```bash
docker build -t safercall-backend:latest .
docker run -d -p 8000:8000 --env-file .env safercall-backend:latest
```

#### Using Docker Compose
```bash
docker-compose up -d
docker-compose logs -f safercall-api
```

### 4. AWS Elastic Beanstalk

#### Prerequisites
```bash
pip install awsebcli
```

#### Initialize
```bash
eb init -p python-3.9 safercall-backend --region us-east-1
```

#### Create Environment
```bash
eb create production --instance-type t3.medium
```

#### Deploy Updates
```bash
eb deploy
```

#### Set Environment Variables
```bash
eb setenv GEMINI_API_KEY=your_key \
         AWS_ACCESS_KEY_ID=your_id \
         AWS_SECRET_ACCESS_KEY=your_secret \
         SECRET_KEY=your_secret_key
```

### 5. AWS Lambda + API Gateway

#### Using Mangum Adapter
```python
# Add to main.py
from mangum import Mangum
handler = Mangum(app)
```

#### Deploy with SAM
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  SaferCallFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: main.handler
      Runtime: python3.9
      Timeout: 30
      MemorySize: 1024
```

### 6. Azure App Service

#### Using Azure CLI
```bash
az webapp up --name safercall-api --runtime "PYTHON:3.9"
az webapp config appsettings set --name safercall-api \
    --settings GEMINI_API_KEY=your_key
```

### 7. Google Cloud Run

```bash
gcloud run deploy safercall-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG_MODE=False`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure logging and monitoring
- [ ] Set up database backups
- [ ] Configure auto-scaling
- [ ] Set up health checks
- [ ] Configure rate limiting
- [ ] Review security settings
- [ ] Set up CI/CD pipeline

## Monitoring

### Application Logs
```bash
tail -f logs/safercall.log
```

### Docker Logs
```bash
docker logs -f safercall-backend
```

### AWS CloudWatch
Configure in AWS Console or using AWS CLI

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (AWS ELB, nginx)
- Multiple application instances
- Session management with Redis

### Vertical Scaling
- Increase instance resources
- Optimize Whisper model size
- Cache frequent requests

## Security Hardening

### Environment Variables
Never commit `.env` to version control

### HTTPS Only
Redirect HTTP to HTTPS in production

### Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### API Key Authentication
Implement API key middleware for production use

---

For detailed troubleshooting, see DOCUMENTATION.md
