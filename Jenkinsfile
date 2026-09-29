pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    triggers { pollSCM('* * * * *') }

    environment {
        IMAGE     = 'lab-python-app'
        TAG       = "${env.BUILD_NUMBER}"
        CONTAINER = 'lab-python-app-c'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Tests and Security Checks') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt pytest bandit pip-audit
                    pytest -q
                    bandit -r . -x ./.venv,./tests -ll
                    pip-audit -r requirements.txt
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest .'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest image \
                      --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed \
                      ${IMAGE}:${TAG}
                '''
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'app-env-file', variable: 'ENV_FILE')]) {
                    sh '''
                        docker rm -f ${CONTAINER} || true
                        docker run -d --name ${CONTAINER} \
                          --restart unless-stopped \
                          --env-file "$ENV_FILE" \
                          -p 9090:8000 \
                          --read-only --tmpfs /tmp \
                          --cap-drop ALL \
                          --security-opt no-new-privileges \
                          ${IMAGE}:${TAG}
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                      curl -fs http://127.0.0.1:9090/health && exit 0
                      sleep 3
                    done
                    docker logs ${CONTAINER}
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
