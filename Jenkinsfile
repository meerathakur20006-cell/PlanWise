
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

        
stage('Deploy Locally') {
    steps {
        echo 'Checking the local PlanWise dashboard'
        bat 'powershell -NoProfile -Command "$response = Invoke-WebRequest -Uri http://127.0.0.1:5000 -UseBasicParsing; if ($response.StatusCode -ne 200) { exit 1 }; Write-Output \'PlanWise dashboard is responding successfully\'"'
    }
}

    }

    post {
        success {
            echo 'PlanWise CI/CD pipeline completed successfully!'
        }
        failure {
            echo 'PlanWise pipeline failed. Check the console output.'
        }
    }
}
