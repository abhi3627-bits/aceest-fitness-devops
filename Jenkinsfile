pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv jenkins-venv'
                sh 'jenkins-venv/bin/pip install --upgrade pip'
                sh 'jenkins-venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Build and Lint') {
            steps {
                sh 'jenkins-venv/bin/python -m py_compile app.py'
            }
        }

        stage('Automated Testing') {
            steps {
                sh 'jenkins-venv/bin/pytest -q'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aceest-fitness:jenkins .'
            }
        }
    }

    post {
        always {
            sh 'rm -rf jenkins-venv'
        }

        success {
            echo 'ACEest Fitness CI pipeline completed successfully.'
        }

        failure {
            echo 'ACEest Fitness CI pipeline failed.'
        }
    }
}
