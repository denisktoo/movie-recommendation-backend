pipeline {
    agent {
        docker {
            image 'python:3.12'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root:root'
        }
    }

    environment {
        VENV_DIR = "env"
        IMAGE_NAME = "kiprotich507/movie-recommendation-backend"
        IMAGE_TAG = "latest"

        USE_SQLITE_FOR_TESTS = 'true'
        SECRET_KEY           = credentials('django-secret-key')
        TMDB_API_KEY         = credentials('tmdb-api-key')
        EMAIL_HOST_PASSWORD  = credentials('email-host-password')
        EMAIL_HOST           = 'smtp.gmail.com'
        EMAIL_PORT           = '587'
        EMAIL_HOST_USER      = 'kiprotichdenis95@gmail.com'
        DEFAULT_FROM_EMAIL   = 'kiprotichdenis95@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/denisktoo/movie-recommendation-backend.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    apt-get update && apt-get install -y gcc libpq-dev docker.io \
                    && rm -rf /var/lib/apt/lists/*

                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip3 install --upgrade pip
                    pip3 install --default-timeout=100 --no-cache-dir -r requirements.txt
                    pip3 install pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    pip3 install pytest-django
                    pytest --junitxml=report.xml
                '''
            }
            post {
                always {
                    junit 'report.xml'
                }
            }
        }

        stage('Get Git Commit Hash') {
            steps {
                script {
                    sh 'git config --global --add safe.directory "$WORKSPACE"'
                    COMMIT_HASH = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = COMMIT_HASH
                    echo "Docker image tag will be: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME:latest -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push $IMAGE_NAME:latest
                        docker push $IMAGE_NAME:$IMAGE_TAG
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
        always {
            cleanWs()
        }
    }
}
