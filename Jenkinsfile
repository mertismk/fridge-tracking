pipeline {
    agent {
        label 'docker'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER} .'
                sh 'docker tag 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER} 51.250.4.236:5000/fridge_planner:latest'
            }
        }

        stage('Push to Local Registry') {
            steps {
                sh 'docker push 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER}'
                sh 'docker push 51.250.4.236:5000/fridge_planner:latest'
            }
        }

        stage('Check Branch Name') {
            steps {
                sh 'echo "Значение BRANCH_NAME: ${env.BRANCH_NAME}"'
            }
        }

        stage('Deploy to Stage') {
            when {
                expression { return env.BRANCH_NAME == 'dev' }
            }
            steps {
                sh '''
                ssh -o StrictHostKeyChecking=no timofey@89.169.142.35 "mkdir -p /home/timofey/fridge_planner"
                scp docker-compose.yml timofey@89.169.142.35:/home/timofey/fridge_planner/
                ssh -o StrictHostKeyChecking=no timofey@89.169.142.35 "cd /home/timofey/fridge_planner && \\
                sed -i 's/mertismk\\/fridge_planner/51.250.4.236:5000\\/fridge_planner:latest/' docker-compose.yml && \\
                docker-compose down && \\
                docker-compose up -d"
                '''
            }
        }
    }
}