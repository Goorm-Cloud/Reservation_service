pipeline {
    agent any
    environment {
        GITNAME = 'rttitity'
        GITMAIL = 'jinwoo25803@gmail.com'
        GITWEBADD = 'https://github.com/Goorm-Cloud/Reservation_service.git'
        GITSSHADD = 'git@github.com:Goorm-Cloud/manifast-reservation.git'
        GITCREDENTIAL = 'git_cre_zinucha'
        ECR_REGISTRY = '651706756261.dkr.ecr.ap-northeast-2.amazonaws.com'
        ECR_REPO = 'reservation_service'
        AWS_CREDENTIAL = 'zinucha_AWS_Credentials'
        DISCORD_WEBHOOK = credentials('jenkins-discord-webhook')
    }

    stages {
        stage('Checkout Application Repository') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
        }

        // ✅ .gitignore을 로컬에서만 적용
        stage('Apply .gitignore Locally') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'gitignore_secret', variable: 'GITIGNORE_CONTENT')]) {
                        sh 'echo "$GITIGNORE_CONTENT" > .gitignore'
                    }
                }
            }
        }

        // ✅ config.py & .env 파일 생성
        stage('Create config.py & .env') {
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'config_secret', variable: 'CONFIG_FILE'),
                        file(credentialsId: 'env_secret', variable: 'ENV_FILE')
                    ]) {
                        sh 'cp $CONFIG_FILE config.py'
                        sh 'cp $ENV_FILE .env'
                        sh 'chmod 600 config.py .env'
                    }
                }
            }
        }

        // ✅ Docker Image 빌드 및 푸시
        stage('AWS ECR Login') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: AWS_CREDENTIAL]]) {
                        sh "aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number} ."
                sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:latest ."
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:latest"
            }
        }

        // ✅ 매니페스트 레포지토리 체크아웃
        stage('Checkout Manifest Repository') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                    userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITSSHADD]]])
                }
            }
        }

        // ✅ 이미지 태그 변경
        stage('Update EKS Manifest') {
            steps {
                script {
                    sh 'git config --local user.email "${GITMAIL}"'
                    sh 'git config --local user.name "${GITNAME}"'

                    // ✅ 최신 변경 사항 가져오기
                    sh "git fetch origin main"
                    sh "git pull --rebase origin main || true"
                    sh "git reset --hard origin/main"

                    // ✅ 최신 커밋 확인
                    sh "git log -n 5 --oneline"

                    // ✅ 이미지 태그 변경 (빌드 번호 적용)
                    sh "sed -i 's@image:.*@image: ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}@g' reservation.yaml"

                    // ✅ 변경 사항 반영 및 push
                    sh "git add reservation.yaml"
                    sh "git commit -m 'Update manifest with new image tag: ${currentBuild.number}'"
                    sh "git push origin main"
                }
            }
        }
    }

    // ✅ 디스코드 알림 (이전 스타일로 복구)
    post {
        success {
            script {
                def discordMessage = """{
                    "username": "Jenkins",
                    "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                    "embeds": [{
                        "title": "✅ Jenkins Build 성공!",
                        "description": "파이프라인 빌드가 성공적으로 완료되었습니다.",
                        "color": 3066993,
                        "fields": [
                            {"name": "프로젝트", "value": "Reservation Service", "inline": true},
                            {"name": "빌드 번호", "value": "${currentBuild.number}", "inline": true},
                            {"name": "ECR 이미지", "value": "${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}", "inline": false},
                            {"name": "커밋 로그", "value": "[GitHub Repository](${GITWEBADD})", "inline": false}
                        ],
                        "footer": {
                            "text": "Jenkins CI/CD",
                            "icon_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png"
                        },
                        "timestamp": "${new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone('UTC'))}"
                    }]
                }"""

                sh "curl -X POST -H 'Content-Type: application/json' -d '${discordMessage}' ${DISCORD_WEBHOOK}"
            }
        }
        failure {
            script {
                def discordMessage = """{
                    "username": "Jenkins",
                    "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                    "embeds": [{
                        "title": "❌ Jenkins Build 실패!",
                        "description": "파이프라인 빌드에 실패하였습니다.",
                        "color": 15158332,
                        "fields": [
                            {"name": "프로젝트", "value": "Reservation Service", "inline": true},
                            {"name": "빌드 번호", "value": "${currentBuild.number}", "inline": true},
                            {"name": "GitHub Repo", "value": "[Repository Link](${GITWEBADD})", "inline": false}
                        ],
                        "footer": {
                            "text": "Jenkins CI/CD",
                            "icon_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png"
                        },
                        "timestamp": "${new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone('UTC'))}"
                    }]
                }"""

                sh "curl -X POST -H 'Content-Type: application/json' -d '${discordMessage}' ${DISCORD_WEBHOOK}"
            }
        }
    }
}