
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out PlanWise source code'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/meerathakur20006-cell/PlanWise.git'
                    ]]
                )
            }
        }

        stage('Setup Python') {
            steps {
                bat 'python --version'
                bat 'python -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '.venv\\Scripts\\python -m pip install --upgrade pip'
                bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '.venv\\Scripts\\python -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'PlanWise CI pipeline completed successfully!'
        }
        failure {
            echo 'PlanWise CI pipeline failed. Check the console output.'
        }
    }
}
