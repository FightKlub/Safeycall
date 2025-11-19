# AWS Deployment Guide - SaferCall AI

## 🚀 Complete AWS Deployment Walkthrough

This guide provides step-by-step instructions for deploying SaferCall AI to AWS using multiple deployment strategies.

---

## 📋 Prerequisites

### 1. AWS Account Setup
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region: us-east-1
# Default output format: json
```

### 2. Create IAM User for Deployment
```bash
# Create IAM user
aws iam create-user --user-name safercall-deployer

# Attach policies
aws iam attach-user-policy \
  --user-name safercall-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy \
  --user-name safercall-deployer \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess
```

---

## 🗂️ Step 1: Set Up S3 Bucket

### Create S3 Bucket:
```bash
# Create bucket
aws s3 mb s3://safercall-audio-storage-prod --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket safercall-audio-storage-prod \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket safercall-audio-storage-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket safercall-audio-storage-prod \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true
```

### Configure Lifecycle Policy:
```bash
# Create lifecycle-policy.json
cat > lifecycle-policy.json << EOF
{
  "Rules": [
    {
      "Id": "DeleteOldAudio",
      "Status": "Enabled",
      "Prefix": "audio/",
      "Expiration": {
        "Days": 90
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ]
    }
  ]
}
EOF

# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket safercall-audio-storage-prod \
  --lifecycle-configuration file://lifecycle-policy.json
```

---

## 🗄️ Step 2: Set Up RDS PostgreSQL

### Create DB Subnet Group:
```bash
# Create subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name safercall-db-subnet \
  --db-subnet-group-description "SaferCall database subnet group" \
  --subnet-ids subnet-12345678 subnet-87654321
```

### Create RDS Instance:
```bash
# Create PostgreSQL database
aws rds create-db-instance \
  --db-instance-identifier safercall-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username safercall_admin \
  --master-user-password "SecureP@ssw0rd2024" \
  --allocated-storage 20 \
  --storage-type gp3 \
  --vpc-security-group-ids sg-database \
  --db-subnet-group-name safercall-db-subnet \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted \
  --no-publicly-accessible

# Wait for creation (takes 5-10 minutes)
aws rds wait db-instance-available --db-instance-identifier safercall-db

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier safercall-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### Initialize Database:
```bash
# Connect to RDS
psql -h safercall-db.xyz.us-east-1.rds.amazonaws.com \
     -U safercall_admin \
     -d postgres

# Run schema creation
\i backend/app/schema.sql
```

---

## 💾 Step 3: Set Up ElastiCache (Redis)

### Create Cache Subnet Group:
```bash
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name safercall-cache-subnet \
  --cache-subnet-group-description "SaferCall cache subnet group" \
  --subnet-ids subnet-12345678 subnet-87654321
```

### Create Redis Cluster:
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id safercall-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name safercall-cache-subnet \
  --security-group-ids sg-cache \
  --port 6379

# Get endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id safercall-cache \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint' \
  --output table
```

---

## 🐳 Deployment Option 1: Elastic Beanstalk

### Install EB CLI:
```bash
pip install awsebcli
```

### Initialize Application:
```bash
cd backend

# Initialize EB
eb init -p python-3.9 safercall-backend \
  --region us-east-1 \
  --keyname safercall-key

# Create environment
eb create safercall-production \
  --instance-type t3.medium \
  --instance-profile SaferCallAppRole \
  --service-role aws-elasticbeanstalk-service-role \
  --envvars \
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE,\
    AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY,\
    AWS_REGION=us-east-1,\
    AWS_S3_BUCKET_NAME=safercall-audio-storage-prod,\
    DATABASE_URL=postgresql://safercall_admin:SecureP@ssw0rd2024@safercall-db.xyz.us-east-1.rds.amazonaws.com:5432/safercall,\
    REDIS_URL=redis://safercall-cache.xyz.cache.amazonaws.com:6379/0,\
    GEMINI_API_KEY=AIzaSyDFEN1_HHBvLlZTXyBKd-tiXSM3p1BUvck

# Deploy application
eb deploy
```

### Configure Load Balancer:
```bash
# Enable HTTPS
eb create safercall-production \
  --elb-type application \
  --ssl-certificate-id arn:aws:acm:us-east-1:...:certificate/...

# Configure health check
eb config --cfg prod-config
```

### Check Status:
```bash
# View environment status
eb status

# Open in browser
eb open

# View logs
eb logs

# SSH to instance
eb ssh
```

---

## ⚡ Deployment Option 2: AWS Lambda + API Gateway

### Install SAM CLI:
```bash
pip install aws-sam-cli
```

### Create SAM Template:
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  GeminiApiKey:
    Type: String
    NoEcho: true

Globals:
  Function:
    Timeout: 30
    MemorySize: 1024
    Environment:
      Variables:
        AWS_S3_BUCKET_NAME: safercall-audio-storage-prod
        GEMINI_API_KEY: !Ref GeminiApiKey

Resources:
  SaferCallApi:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: main.handler
      Runtime: python3.9
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
      Policies:
        - S3CrudPolicy:
            BucketName: safercall-audio-storage-prod
        - CloudWatchPutMetricPolicy: {}

Outputs:
  ApiUrl:
    Description: "API Gateway endpoint"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

### Deploy with SAM:
```bash
# Build
sam build

# Deploy
sam deploy \
  --guided \
  --stack-name safercall-lambda \
  --parameter-overrides GeminiApiKey=AIzaSyDFEN1_HHBvLlZTXyBKd-tiXSM3p1BUvck

# Get API URL
aws cloudformation describe-stacks \
  --stack-name safercall-lambda \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

---

## 🐋 Deployment Option 3: Amazon ECS (Fargate)

### Build and Push Docker Image:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository \
  --repository-name safercall-api \
  --region us-east-1

# Build image
docker build -t safercall-api backend/

# Tag image
docker tag safercall-api:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/safercall-api:latest

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/safercall-api:latest
```

### Create ECS Cluster:
```bash
# Create cluster
aws ecs create-cluster --cluster-name safercall-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster safercall-cluster \
  --service-name safercall-api-service \
  --task-definition safercall-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-app],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=safercall-api,containerPort=8000"
```

---

## 🖥️ Deployment Option 4: EC2 with Docker Compose

### Launch EC2 Instance:
```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name safercall-key \
  --query 'KeyMaterial' \
  --output text > safercall-key.pem

chmod 400 safercall-key.pem

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name safercall-key \
  --security-group-ids sg-app \
  --subnet-id subnet-12345678 \
  --iam-instance-profile Name=SaferCallAppRole \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=SaferCall-API}]'
```

### User Data Script (user-data.sh):
```bash
#!/bin/bash

# Update system
yum update -y

# Install Docker
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
cd /home/ec2-user
git clone https://github.com/FightKlub/Safeycall.git
cd Safeycall

# Create .env file
cat > backend/.env << EOF
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=safercall-audio-storage-prod
DATABASE_URL=postgresql://safercall_admin:SecureP@ssw0rd2024@safercall-db.xyz.us-east-1.rds.amazonaws.com:5432/safercall
REDIS_URL=redis://safercall-cache.xyz.cache.amazonaws.com:6379/0
GEMINI_API_KEY=AIzaSyDFEN1_HHBvLlZTXyBKd-tiXSM3p1BUvck
ENVIRONMENT=production
EOF

# Start services
docker-compose up -d

# Enable auto-start
cat > /etc/systemd/system/safercall.service << EOF
[Unit]
Description=SaferCall API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/Safeycall
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl enable safercall
```

### Connect and Verify:
```bash
# Get instance public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=SaferCall-API" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# SSH to instance
ssh -i safercall-key.pem ec2-user@<PUBLIC_IP>

# Check logs
docker-compose logs -f api
```

---

## 📊 Step 4: Configure CloudWatch Monitoring

### Create Log Groups:
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/safercall/api
aws logs create-log-group --log-group-name /aws/safercall/errors

# Set retention
aws logs put-retention-policy \
  --log-group-name /aws/safercall/api \
  --retention-in-days 30
```

### Create CloudWatch Alarms:
```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name safercall-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:...:alerts

# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name safercall-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## 🔒 Step 5: Enable AWS WAF (Optional)

### Create Web ACL:
```bash
# Create web ACL
aws wafv2 create-web-acl \
  --name safercall-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json \
  --visibility-config \
    SampledRequestsEnabled=true,\
    CloudWatchMetricsEnabled=true,\
    MetricName=SaferCallWAF

# Associate with ALB
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:...:regional/webacl/safercall-waf/... \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:...:loadbalancer/app/...
```

---

## ✅ Step 6: Verify Deployment

### Test Endpoints:
```bash
# Get API URL (from EB, Lambda, or ALB)
API_URL="https://safercall-production.us-east-1.elasticbeanstalk.com"

# Health check
curl $API_URL/health

# Test scan
curl -X POST $API_URL/api/scan/text \
  -H "Content-Type: application/json" \
  -d '{"text": "You won $1,000,000! Call now!"}'

# Check stats
curl $API_URL/api/stats
```

### Monitor Logs:
```bash
# CloudWatch Logs Insights query
aws logs start-query \
  --log-group-name /aws/safercall/api \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 20'
```

---

## 🎯 Post-Deployment Checklist

- [ ] S3 bucket created with encryption enabled
- [ ] RDS PostgreSQL instance running with Multi-AZ
- [ ] ElastiCache Redis cluster available
- [ ] Application deployed and responding to health checks
- [ ] CloudWatch alarms configured
- [ ] IAM roles and policies properly configured
- [ ] Security groups configured correctly
- [ ] SSL/TLS certificate installed (HTTPS)
- [ ] Auto-scaling policies configured
- [ ] Backup strategy implemented
- [ ] Cost monitoring enabled
- [ ] Documentation updated with endpoints

---

## 🚨 Troubleshooting

### Common Issues:

**1. Application won't start:**
```bash
# Check logs
eb logs
# or
docker-compose logs api

# Verify environment variables
eb printenv
```

**2. Can't connect to RDS:**
```bash
# Check security group
aws ec2 describe-security-groups --group-ids sg-database

# Test connection
telnet safercall-db.xyz.us-east-1.rds.amazonaws.com 5432
```

**3. S3 permissions error:**
```bash
# Verify IAM role
aws iam get-role --role-name SaferCallAppRole

# Test S3 access
aws s3 ls s3://safercall-audio-storage-prod/
```

---

## 📞 Support

For deployment assistance:
- GitHub Issues: https://github.com/FightKlub/Safeycall/issues
- AWS Support: https://console.aws.amazon.com/support/

**🎉 Deployment Complete! Your SaferCall AI is now running on AWS!**
