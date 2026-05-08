# Fraud Detection MLOps Monitoring Project

Complete MLOps monitoring solution for fraud detection with automated drift detection, alerting, and retraining.

## 🏗️ Project Structure

```
mlops-monitoring-project/
├── notebooks/                    # Jupyter notebooks for each phase
│   ├── 01_data_generation.ipynb     # Generate synthetic fraud data
│   ├── 02_model_training.ipynb      # Train fraud detection model
│   ├── 03_model_deployment.ipynb    # Deploy with monitoring
│   ├── 04_create_baseline.ipynb     # Create monitoring baseline
│   └── 05_test_drift_detection.ipynb # Test drift simulation
├── src/                          # Source code
│   ├── training/                    # Model training
│   │   └── fraud_train.py
│   ├── inference/                   # Model inference
│   │   └── fraud_inference.py
│   ├── monitoring/                  # Monitoring components
│   │   ├── setup_monitoring.py
│   │   ├── setup_alerts.py
│   │   ├── slack_alerts.py
│   │   └── create_dashboard.py
│   ├── processing/                  # Data processing
│   │   └── prepare_data.py
│   ├── evaluation/                  # Model evaluation
│   │   └── evaluate.py
│   └── pipelines/                   # MLOps pipelines
│       └── retraining_pipeline.py
├── infrastructure/               # Infrastructure setup
│   ├── main.tf                     # Terraform configuration
│   └── setup.py                    # Python setup script
├── config/                       # Configuration
│   └── config.py
└── data/                        # Data storage
    ├── raw/
    └── processed/
```

## 🚀 Quick Start

### Phase 1: Setup Infrastructure (Week 1)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup AWS Infrastructure**
   ```bash
   cd infrastructure
   python setup.py
   # Or use Terraform
   terraform init && terraform apply
   ```

3. **Update Configuration**
   Edit `config/config.py` with your AWS settings

### Phase 2: Data & Training (Week 2)

4. **Generate Dataset**
   ```bash
   jupyter notebook notebooks/01_data_generation.ipynb
   ```

5. **Train Model**
   ```bash
   jupyter notebook notebooks/02_model_training.ipynb
   ```

### Phase 3: Deployment & Monitoring (Week 3)

6. **Deploy Model**
   ```bash
   jupyter notebook notebooks/03_model_deployment.ipynb
   ```

7. **Create Baseline**
   ```bash
   jupyter notebook notebooks/04_create_baseline.ipynb
   ```

### Phase 4: Alerting (Week 4)

8. **Setup Alerts**
   ```python
   from src.monitoring.setup_alerts import setup_alerts
   setup_alerts('your-endpoint-name', 'your-email@example.com')
   ```

### Phase 5: Testing (Week 5-7)

9. **Test Drift Detection**
   ```bash
   jupyter notebook notebooks/05_test_drift_detection.ipynb
   ```

## 📊 Features

### Core Monitoring
- **Data Drift Detection**: Automated monitoring using SageMaker Model Monitor
- **Performance Tracking**: Real-time model performance metrics
- **Automated Alerting**: CloudWatch alarms with SNS/Slack integration

### Fraud Detection Specific
- **Synthetic Dataset**: 50K samples with 5% fraud rate
- **Feature Engineering**: 20 meaningful fraud detection features
- **Balanced Training**: Class-weighted Random Forest model

### MLOps Pipeline
- **Automated Retraining**: SageMaker Pipelines with quality gates
- **Model Evaluation**: AUC threshold-based approval
- **Infrastructure as Code**: Terraform for AWS resources

### Visualization
- **CloudWatch Dashboards**: Real-time monitoring dashboards
- **Drift Visualization**: Feature drift tracking
- **Performance Metrics**: Model accuracy and latency tracking

## 🔧 Configuration

Update these values in `config/config.py`:

```python
# AWS Configuration
aws_region = "us-east-1"
s3_bucket = "your-mlops-monitoring-bucket"
sagemaker_role = "arn:aws:iam::ACCOUNT:role/MLOpsMonitoringRole"

# Model Configuration
endpoint_name = "fraud-detection-endpoint"
monitoring_schedule_name = "fraud-monitoring-schedule"
```

## 📈 Monitoring Metrics

### Model Performance
- Invocations per minute
- Model latency (P50, P90, P99)
- Error rates (4XX, 5XX)

### Data Quality
- Feature baseline drift distance
- Data quality violations
- Missing value rates

### Business Metrics
- Fraud detection rate
- False positive rate
- Model confidence distribution

## 🚨 Alerting

### CloudWatch Alarms
- Data drift threshold: 0.1
- Error rate threshold: 5 errors in 5 minutes
- Latency threshold: 1000ms P99

### Notification Channels
- Email via SNS
- Slack via Lambda webhook
- CloudWatch dashboard alerts

## 🔄 Automated Retraining

### Triggers
- Data drift detection
- Performance degradation
- Scheduled weekly runs

### Quality Gates
- Minimum AUC score: 0.8
- Maximum drift distance: 0.15
- Error rate below 1%

## 📝 Usage Examples

### Send Prediction Request
```python
import boto3
import json

runtime = boto3.client('sagemaker-runtime')
response = runtime.invoke_endpoint(
    EndpointName='fraud-detection-endpoint',
    ContentType='application/json',
    Body=json.dumps({
        'transaction_amount': 100.0,
        'account_age_days': 365,
        # ... other features
    })
)
```

### Check Monitoring Status
```python
from src.monitoring.setup_monitoring import get_monitoring_results
results = get_monitoring_results(monitor)
print(results)
```

## 🛠️ Troubleshooting

### Common Issues
1. **S3 Permissions**: Ensure SageMaker role has S3 access
2. **Endpoint Errors**: Check CloudWatch logs for details
3. **Monitoring Delays**: Allow 1-2 hours for first results

### Debug Commands
```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name your-endpoint

# View monitoring schedule
aws sagemaker describe-monitoring-schedule --monitoring-schedule-name your-schedule

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/SageMaker
```

## 📚 Next Steps

1. **Custom Metrics**: Add business-specific monitoring
2. **A/B Testing**: Implement model comparison
3. **Real-time Features**: Add streaming data processing
4. **Advanced Drift**: Implement statistical drift tests
5. **Model Registry**: Add model versioning and approval

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details