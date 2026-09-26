pipeline {
    agent any

    // Tên project cố định để Jenkins deploy đúng bộ container mà bạn chạy tay,
    // không tạo ra một stack song song.
    environment {
        COMPOSE_PROJECT = 'langgraph-rag-agent'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Tự động build khi có commit mới trên GitHub.
    // Jenkins chạy local nên GitHub không gọi thẳng vào được -> dùng SCM polling:
    // cứ mỗi 3 phút Jenkins hỏi GitHub xem có commit mới không.
    triggers {
        pollSCM('H/3 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare .env') {
            steps {
                // File .env được lưu an toàn trong Jenkins Credentials (Secret file),
                // không nằm trong Git. Ở đây copy nó vào workspace để docker compose đọc.
                withCredentials([file(credentialsId: 'langgraph-env', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                }
            }
        }

        stage('Build images') {
            steps {
                sh 'docker compose -p "$COMPOSE_PROJECT" build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose -p "$COMPOSE_PROJECT" up -d'
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    echo "Đợi backend healthy..."
                    for i in $(seq 1 30); do
                        status=$(docker inspect --format '{{.State.Health.Status}}' langgraph_backend 2>/dev/null || echo "starting")
                        echo "  [$i] backend = $status"
                        if [ "$status" = "healthy" ]; then
                            echo "Backend healthy!"
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Backend không healthy sau 150s - xem log:"
                    docker logs --tail 50 langgraph_backend
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build & deploy thành công. App: http://localhost:8501'
        }
        failure {
            echo '❌ Pipeline thất bại. Kiểm tra log ở trên.'
        }
        always {
            // Dọn workspace .env để không sót secret
            sh 'rm -f .env || true'
        }
    }
}
