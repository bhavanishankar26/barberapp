pipeline {
    agent any

    environment {
        WEB_CONTAINER_NAME = 'barberapp-backend_shop-module-web-1'
        DB_CONTAINER_NAME = 'barberapp-backend_shop-module-db-1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scmGit(branches: [[name: '**']], extensions: [], userRemoteConfigs: [[credentialsId: 'github', url: 'https://github.com/Hashtek-Solutions/barberapp-backend.git']])
            }
        }

        stage('Stop Existing Containers') {
            steps {
                script {
                    // Stop and remove the web container if it's running
                    def webContainerRunning = sh(script: "docker ps -q -f name=${WEB_CONTAINER_NAME}", returnStdout: true).trim()
                    if (webContainerRunning) {
                        echo "Stopping and removing the existing web container..."
                        sh "docker stop ${WEB_CONTAINER_NAME}"
                        sh "docker rm ${WEB_CONTAINER_NAME}"
                    } else {
                        echo "No existing web container running."
                    }

                    // Stop and remove the database container if it's running (Optional)
                    def dbContainerRunning = sh(script: "docker ps -q -f name=${DB_CONTAINER_NAME}", returnStdout: true).trim()
                    if (dbContainerRunning) {
                        echo "Stopping and removing the existing database container..."
                        sh "docker stop ${DB_CONTAINER_NAME}"
                        sh "docker rm ${DB_CONTAINER_NAME}"
                    } else {
                        echo "No existing database container running."
                    }
                }
            }
        }

        stage('Build and Deploy') {
            steps {
                echo 'Deploying the new version...'
                dir('barberapp-backend') { // Change to the repository directory
                    sh "docker-compose up -d"
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            deleteDir()
        }
        success {
            echo 'Deployment succeeded!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
