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

        stage('Deploy to Stage') {
            when {
                expression { return env.GIT_BRANCH == 'origin/dev' }
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'timofey-stage-deploy-key', keyFileVariable: 'SSH_KEY_FILE')]) {
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"mkdir -p /home/timofey/fridge_planner\""""
                    
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"ls -ld /home/timofey/fridge_planner\""""
                    
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"rm -rf /home/timofey/fridge_planner/db_init.sql\""""
                    
                    sh """scp -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv docker-compose.yml db_init.sql timofey@89.169.142.35:/home/timofey/fridge_planner/"""
                    
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"
                        cd /home/timofey/fridge_planner && \\
                        echo 'Attempting to modify docker-compose.yml...' && \\
                        sed -i 's/mertismk\\\\/fridge_planner/51.250.4.236:5000\\\\/fridge_planner:latest/' docker-compose.yml && \\
                        echo 'Attempting docker-compose down...' && \\
                        docker-compose down && \\
                        echo 'Attempting docker-compose up -d...' && \\
                        docker-compose up -d --force-recreate && \\
                        echo 'Deployment commands finished.'\""""
                }
            }
        }
    }
}