Goal: Every time you push to GitHub main, Jenkins will:
1.	Checkout code from GitHub
2.	Build Docker image for the Flask app
3.	Run basic checks (lint/health/test or at least container boot + /health)
4.	Push image to AWS ECR
5.	Deploy on an EC2 host (same instance or a separate “deploy EC2”) using Docker Compose pulling the new ECR image
6.	Verify deployment by calling the public endpoint
Why ECR + Jenkins?
•	ECR is AWS-native container registry: secure, IAM-controlled, reliable.
•	Jenkins orchestrates build + push + deploy, and gives you logs, history, rollback capability.

1) Architecture you are building (what Jenkins will do)
Pipeline stages (industry standard)
1.	Checkout: pull code from GitHub
2.	Build: build Docker image for the Flask web service
3.	Test: run basic checks (lint/unit tests/health check)
4.	Scan (optional but recommended): vulnerability scan of image (Trivy)
5.	Push: push image to AWS ECR
6.	Deploy: SSH to “App EC2” and update docker compose to pull the new image, then restart
This gives you repeatable deployments and removes “manual install/run” friction.

1️⃣ Application Layer
•	Flask two-tier web application
•	Backend: MySQL
•	Frontend: Flask + HTML
•	Production server: Gunicorn
 
2️⃣ Containerization
•	Dockerized Flask application
•	Multi-container setup using Docker Compose
•	MySQL container with persistent volume
•	Health checks and environment variables
 
3️⃣ Source Control
•	GitHub repository
•	Jenkinsfile stored in repo (Pipeline-as-Code)
•	Clean commit history


CI/CD Pipeline (CORE ACHIEVEMENT)
You implemented real CI/CD, not a demo.
Pipeline stages:
1.	Checkout code from GitHub
2.	Build Docker image
3.	Authenticate to AWS ECR
4.	Push versioned + latest image to ECR
5.	SSH into App EC2
6.	Pull new image
7.	Restart services via Docker Compose
8.	Auto-cleanup unused images
 
5️⃣ AWS Infrastructure
•	EC2 (Jenkins Server)
•	EC2 (Application Server)
•	AWS ECR (private container registry)
•	Secure IAM user + credentials
•	SSH key-based access
•	Proper security group configuration
 
6️⃣ Jenkins
•	Installed & configured Jenkins manually
•	Credential management:
o	AWS access keys
o	EC2 SSH key
•	Pipeline job using Pipeline from SCM
•	Successful build execution visible on dashboard
