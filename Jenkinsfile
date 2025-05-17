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
                sh 'mkdir -p reports'
                
                sh '''
                    docker run --rm -v "${WORKSPACE}:/app" -w /app python:3.9-slim bash -c "
                        echo 'Установка Python зависимостей...' && 
                        pip install -r requirements.txt pytest pytest-cov pytest-mock requests-mock werkzeug==2.0.1 && 
                        
                        echo 'Запуск тестов с покрытием кода...' &&
                        python -m pytest tests/test_models.py tests/test_utils.py tests/test_routes.py --cov=app --cov-report=xml:/app/reports/coverage.xml --cov-report=html:/app/reports/coverage_html --junitxml=/app/reports/pytest_results.xml -v &&
                        
                        echo 'Проверка созданных отчетов:' &&
                        ls -la /app/reports/
                    "
                '''
            }
            post {
                always {
                    junit(testResults: 'reports/pytest_results.xml', allowEmptyResults: true)
                    publishHTML (target : [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Run Failing Test') {
            agent { label 'docker' }
            when {
                branch 'feature/*'
            }
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh """
                        docker run --rm -v "${WORKSPACE}":/app -w /app python:3.9-slim sh -c " 
                            echo \"Установка Python зависимостей...\" && 
                            pip install --no-cache-dir -r requirements.txt && 
                            pip install pytest && 
                            echo \"Запуск тестов, которые должны провалиться...\" && 
                            python -m pytest tests/test_failing.py -v
                        "
                    """
                }
                echo "Тест намеренно провален для демонстрации неуспешного прохождения (только для feature веток)"
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
            node(label: 'docker') {
                echo 'Archiving reports...'
                archiveArtifacts artifacts: 'reports/**', fingerprint: true
            }
        }
    }
}