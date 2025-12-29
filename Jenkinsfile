pipeline {
  agent any

  environment {
    AWS_REGION   = "us-east-1"
    ECR_REPO     = "two-tier-webapp"
    ECR_REGISTRY = "236195543546.dkr.ecr.us-east-1.amazonaws.com"
    IMAGE_URI    = "${ECR_REGISTRY}/${ECR_REPO}"
    APP_HOST     = "ec2-3-90-110-123.compute-1.amazonaws.com"
  }

  stages {
    stage("Checkout") {
      steps { checkout scm }
    }

    stage("Build Docker image") {
      steps {
        sh """
          docker build -t ${IMAGE_URI}:${BUILD_NUMBER} -t ${IMAGE_URI}:latest ./app
        """
      }
    }

    stage("Login to ECR") {
      steps {
        withCredentials([usernamePassword(credentialsId: 'aws-access-key',
          usernameVariable: 'AWS_ACCESS_KEY_ID',
          passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {

          sh """
            aws ecr get-login-password --region ${AWS_REGION} \
              | docker login --username AWS --password-stdin ${ECR_REGISTRY}
          """
        }
      }
    }

    stage("Push image to ECR") {
      steps {
        sh """
          docker push ${IMAGE_URI}:${BUILD_NUMBER}
          docker push ${IMAGE_URI}:latest
        """
      }
    }

    stage("Deploy to App EC2") {
      steps {
        sshagent(credentials: ['app-ec2-ssh']) {
          sh """
            ssh -o StrictHostKeyChecking=no ubuntu@${APP_HOST} '
              set -e
              aws ecr get-login-password --region ${AWS_REGION} \
                | docker login --username AWS --password-stdin ${ECR_REGISTRY}

              cd ~/projects/two_tier_webapp
              docker pull ${IMAGE_URI}:latest
              docker compose down
              docker compose up -d
              docker ps
            '
          """
        }
      }
    }
  }

  post {
    always {
      sh "docker image prune -f || true"
    }
  }
}
