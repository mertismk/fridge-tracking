pipeline {
    agent none

    stages {
        stage('Checkout') {
            agent any
            steps {
                checkout scm
            }
        }

        stage('Run Tests & Analysis') {
            agent { label 'docker' }
            steps {
                sh \"\"\"\n                    docker run --rm -v \"${WORKSPACE}\":/app -w /app python:3.9-slim sh -c \" \\\n                        apt-get update && apt-get install -y wget tar && \\\n                        echo \\\"Установка Gitleaks...\\\" && \\\n                        GITLEAKS_VERSION='8.24.3' && \\\n                        ARCH='x64' && \\\n                        wget \\\"https://github.com/gitleaks/gitleaks/releases/download/v\${GITLEAKS_VERSION}/gitleaks_\${GITLEAKS_VERSION}_linux_\${ARCH}.tar.gz\\\" -O gitleaks.tar.gz && \\\n                        tar -xzf gitleaks.tar.gz gitleaks && \\\n                        rm gitleaks.tar.gz && \\\n                        chmod +x gitleaks && \\\n                        mv gitleaks /usr/local/bin/ && \\\n                        echo \\\"Установка Python зависимостей...\\\" && \\\n                        pip install --no-cache-dir -r requirements.txt && \\\n                        echo \\\"Запуск скрипта анализа...\\\" && \\\n                        chmod +x scripts/run_analysis.sh && \\\n                        ./scripts/run_analysis.sh \\\n                    \"\n                \"\"\"
            }
        }

        stage('Build') {
            agent { label 'docker' }
            steps {
                sh 'docker build -t 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER} .'
                sh 'docker tag 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER} 51.250.4.236:5000/fridge_planner:latest'
            }
        }

        stage('Push to Local Registry') {
            agent { label 'docker' }
            steps {
                sh 'docker push 51.250.4.236:5000/fridge_planner:${BUILD_NUMBER}'
                sh 'docker push 51.250.4.236:5000/fridge_planner:latest'
            }
        }

        stage('Deploy to Stage') {
            agent { label 'docker' }
            when {
                expression { return env.GIT_BRANCH == 'origin/dev' }
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'timofey-stage-deploy-key', keyFileVariable: 'SSH_KEY_FILE')]) {
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"mkdir -p /home/timofey/fridge_planner\""""
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"ls -ld /home/timofey/fridge_planner\""""
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"rm -rf /home/timofey/fridge_planner/db_init.sql\""""
                    sh """scp -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv docker-compose.yml timofey@89.169.142.35:/home/timofey/fridge_planner/"""
                    sh """ssh -i $SSH_KEY_FILE -o StrictHostKeyChecking=no -vvv timofey@89.169.142.35 \"
                        cd /home/timofey/fridge_planner && \\
                        echo 'Attempting to modify docker-compose.yml...' && \\
                        sed -i 's/mertismk\\/fridge_planner/51.250.4.236:5000\\/fridge_planner:latest/' docker-compose.yml && \\
                        echo 'Attempting docker-compose down...' && \\
                        docker-compose down && \\
                        echo 'Attempting docker-compose up -d...' && \\
                        docker-compose up -d --force-recreate --pull always && \\
                        echo 'Deployment commands finished.'\""""
                }
            }
        }
    }
    post {
        always {
            // Запускаем post-действия на агенте, чтобы получить доступ к workspace
            node(label: 'docker') {
                echo 'Archiving reports...'
                archiveArtifacts artifacts: 'reports/**', fingerprint: true
            }
        }
    }
}