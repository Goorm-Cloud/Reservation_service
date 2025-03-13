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
        stage('Checkout Github') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
        }

        stage('Create config.py & .env') {
            steps {
                script {
                    sh 'chmod -R 777 $WORKSPACE'
                    withCredentials([
                        file(credentialsId: 'config_secret', variable: 'CONFIG_FILE'),
                        file(credentialsId: 'env_secret', variable: 'ENV_FILE')
                    ]) {
                        sh 'cp $CONFIG_FILE $WORKSPACE/config.py'
                        sh 'cp $ENV_FILE $WORKSPACE/.env'
                        sh 'chmod 600 $WORKSPACE/config.py $WORKSPACE/.env'
                    }
                }
            }
        }

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

        // ✅ workspace 정리 (매니페스트 레포지토리 checkout 전)
        stage('Clean Workspace for Manifest Repo') {
            steps {
                script {
                    deleteDir()  // 기존 workspace 삭제
                }
            }
        }

        stage('Checkout Manifest Repository') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                    userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITSSHADD]]])
                }
            }
        }

        stage('EKS manifest file update') {
            steps {
                script {
                    sh "git config --local user.email ${GITMAIL}"
                    sh "git config --local user.name ${GITNAME}"

                    // 최신 상태 유지
                    sh "git fetch origin main"
                    sh "git reset --hard origin/main"

                    // 이미지 태그 업데이트
                    sh "sed -i 's@image:.*@image: ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}@g' reservation.yaml"

                    // 변경사항 커밋 & 푸시
                    sh "git add reservation.yaml"
                    sh "git commit -m 'Update manifest with new image tag: ${currentBuild.number}'"
                    sh "git push origin main"
                }
            }
        }

        // ✅ 매니페스트 파일 업로드 후 reservation_service 삭제
        stage('Clean Workspace After Manifest Update') {
            steps {
                script {
                    deleteDir()  // workspace 정리
                }
            }
        }
    }

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