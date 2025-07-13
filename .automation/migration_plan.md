# AWS Migration Plan - Medicine Donation System

## Overview
Migrate from local Minikube to AWS using free tier resources with local Jenkins for CI/CD automation.

**Target Architecture:**
- Local Jenkins (always running) → AWS (on-demand)
- Single EC2 t3.micro with MicroK8s
- RDS MySQL db.t3.micro
- Complete infrastructure automation via Terraform
- Application deployment via Helmfile

---

## Phase 1: Local Development Foundation (Week 1)

### 1.1 Update Django for AWS RDS
**Goal:** Make Django compatible with MySQL and environment-based configuration

**Tasks:**
- [ ] Update `settings.py` to use environment variables for database config
- [ ] Install `mysqlclient` or `PyMySQL` for MySQL support
- [ ] Create `.env.example` file with required environment variables
- [ ] Test locally with MySQL database (simulating RDS)
- [ ] Update Django migrations to work with MySQL
- [ ] Test database operations (create, read, update, delete)

**Files to modify:**
- `Medicine_Donation_System_for_NGOs/settings.py`
- `requirements.txt`
- `.env.example` (new file)

### 1.2 Create Helmfile Charts
**Goal:** Convert existing K8s YAML to parameterized Helm charts

**Tasks:**
- [ ] Create `charts/` directory structure
- [ ] Convert `deployment.yaml` to Helm template
- [ ] Convert `service.yaml` to Helm template
- [ ] Convert `storage.yaml` to Helm template
- [ ] Create `values.yaml` files for different environments
- [ ] Create main `helmfile.yaml` configuration
- [ ] Test Helmfile deployment locally with Minikube

**Directory structure to create:**
```
helmfile/
├── helmfile.yaml
├── charts/
│   └── django-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           └── storage.yaml
└── environments/
    ├── local/
    │   └── values.yaml
    └── aws/
        └── values.yaml
```

### 1.3 Test MicroK8s Compatibility
**Goal:** Ensure K8s configs work with MicroK8s (different from Minikube)

**Tasks:**
- [ ] Install MicroK8s locally (if possible) or use VM
- [ ] Test storage class compatibility
- [ ] Verify Helmfile deployment works on MicroK8s
- [ ] Document any MicroK8s-specific configurations needed
- [ ] Test HPA prerequisites (metrics-server addon)

---

## Phase 2: Infrastructure as Code (Week 2)

### 2.1 Basic Terraform Configuration
**Goal:** Create minimal AWS infrastructure for free tier

**Tasks:**
- [ ] Set up Terraform directory structure
- [ ] Create VPC with public/private subnets
- [ ] Create security groups (EC2, RDS, ALB)
- [ ] Create EC2 instance (t3.micro) with Ubuntu
- [ ] Create RDS MySQL instance (db.t3.micro)
- [ ] Create user data script to install MicroK8s on EC2
- [ ] Add outputs for EC2 IP and RDS endpoint
- [ ] Test `terraform plan` and `terraform apply` locally

**Directory structure to create:**
```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── vpc.tf
├── ec2.tf
├── rds.tf
├── security_groups.tf
├── user_data.sh
└── terraform.tfvars.example
```

### 2.2 Advanced Terraform Features
**Goal:** Add production-ready features while staying in free tier

**Tasks:**
- [ ] Add Application Load Balancer (if needed, or use NodePort)
- [ ] Configure Route53 hosted zone for DNS
- [ ] Add IAM roles for EC2 instance
- [ ] Configure automatic MicroK8s setup via user data
- [ ] Add Terraform state management (S3 backend if desired)
- [ ] Test complete infrastructure creation and destruction

---

## Phase 3: Jenkins CI/CD Setup (Week 3)

### 3.1 Local Jenkins Installation
**Goal:** Set up Jenkins locally with required tools

**Tasks:**
- [ ] Install Jenkins locally (Docker recommended)
- [ ] Install required plugins:
  - AWS CLI Plugin
  - Terraform Plugin
  - Kubernetes CLI Plugin
  - Credentials Plugin
- [ ] Install tools in Jenkins container:
  - Terraform
  - kubectl
  - Helmfile
  - AWS CLI
- [ ] Configure AWS credentials in Jenkins
- [ ] Test basic connectivity to AWS

**Jenkins setup commands:**
```bash
# Run Jenkins in Docker
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  jenkins/jenkins:lts
```

### 3.2 Create Jenkins Pipeline
**Goal:** Automate entire deployment process

**Tasks:**
- [ ] Create Jenkinsfile with stages:
  - Infrastructure creation (Terraform)
  - kubectl configuration for remote MicroK8s
  - Application deployment (Helmfile)
  - Optional: Infrastructure destruction
- [ ] Set up parameterized builds
- [ ] Add approval steps for destruction
- [ ] Test full pipeline end-to-end
- [ ] Add error handling and rollback procedures

**Pipeline stages:**
1. Checkout code
2. Terraform init & apply
3. Configure kubectl for remote cluster
4. Helmfile sync
5. Smoke tests
6. Manual approval for destruction
7. Cleanup (optional)

### 3.3 Integration Testing
**Goal:** Validate complete automation workflow

**Tasks:**
- [ ] Test full deployment cycle: create → deploy → test → destroy
- [ ] Verify application accessibility from internet
- [ ] Test database connectivity and data persistence
- [ ] Validate cost monitoring (should stay in free tier)
- [ ] Document troubleshooting steps

---

## Phase 4: Production Features (Week 4)

### 4.1 Horizontal Pod Autoscaler (HPA)
**Goal:** Add auto-scaling capabilities

**Tasks:**
- [ ] Enable metrics-server in MicroK8s via Terraform user data
- [ ] Add HPA configuration to Helm charts
- [ ] Configure resource requests/limits in deployment
- [ ] Test HPA scaling behavior
- [ ] Add HPA to Helmfile templates

### 4.2 DNS and Monitoring
**Goal:** Add production-like features

**Tasks:**
- [ ] Configure Route53 DNS (if within free tier)
- [ ] Add SSL/TLS certificates (Let's Encrypt)
- [ ] Set up basic monitoring/health checks
- [ ] Add ingress controller to MicroK8s
- [ ] Configure load balancer (ALB or nginx ingress)

### 4.3 Documentation and Cleanup
**Goal:** Prepare for showcase

**Tasks:**
- [ ] Update README with deployment instructions
- [ ] Document cost analysis and free tier usage
- [ ] Create demo script for showcasing
- [ ] Test complete deployment from scratch
- [ ] Create troubleshooting guide
- [ ] Add security best practices documentation

---

## Quick Reference Commands

### Development Testing:
```bash
# Test Helmfile locally
helmfile -e local sync

# Test Terraform
cd terraform && terraform plan

# Test Jenkins pipeline locally
# (Use Blue Ocean or classic UI)
```

### AWS Deployment:
```bash
# Manual deployment (for testing)
cd terraform && terraform apply
# Get EC2 IP and configure kubectl
kubectl config set-cluster aws-microk8s --server=https://<EC2-IP>:16443
helmfile -e aws sync
```

### Cleanup:
```bash
# Destroy everything
cd terraform && terraform destroy
```

---

## Success Criteria

### Phase 1 Complete:
- [ ] Django works with MySQL
- [ ] Helmfile deploys successfully to local cluster
- [ ] MicroK8s compatibility verified

### Phase 2 Complete:
- [ ] Terraform creates full AWS infrastructure
- [ ] EC2 has working MicroK8s installation
- [ ] RDS MySQL is accessible from EC2

### Phase 3 Complete:
- [ ] Jenkins can deploy complete stack to AWS
- [ ] Application is accessible from internet
- [ ] Full automation works: deploy → test → destroy

### Phase 4 Complete:
- [ ] HPA scales pods based on load
- [ ] DNS provides friendly URL access
- [ ] Ready for professional showcase

---

## Estimated Timeline: 3-4 weeks
- **Week 1:** Application prep and local testing
- **Week 2:** Infrastructure automation
- **Week 3:** CI/CD integration
- **Week 4:** Production features and polish

## Cost Estimation:
- **Monthly (if left running):** ~$0 (within free tier limits)
- **Per demo session:** ~$0.10-0.50 (few hours of usage)
- **Storage:** ~$2-3/month for RDS if exceeding free tier
