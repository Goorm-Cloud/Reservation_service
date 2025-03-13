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
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
        }

        // ✅ .gitignore 파일 적용
        stage('Apply .gitignore from Credentials') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'gitignore_secret', variable: 'GITIGNORE_CONTENT')]) {
                        sh 'echo "$GITIGNORE_CONTENT" > $WORKSPACE/.gitignore'
                        sh 'git update-index --assume-unchanged $WORKSPACE/.gitignore'
                    }
                }
            }
        }

        // ✅ config.py & .env 생성 (Secret File 활용)
        stage('Create config.py & .env') {
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'config_secret', variable: 'CONFIG_FILE'),
                        file(credentialsId: 'env_secret', variable: 'ENV_FILE')
                    ]) {
                        sh 'cp $CONFIG_FILE $WORKSPACE/config.py'
                        sh 'cp $ENV_FILE $WORKSPACE/.env'
                        sh 'chmod 600 $WORKSPACE/config.py'
                        sh 'chmod 600 $WORKSPACE/.env'
                    }
                }
            }
        }

        // ✅ Docker Image 빌드 및 Push
        stage('Build & Push Docker Image') {
            steps {
                script {
                    sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number} ."
                    sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                }
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
        stage('EKS manifest file update') {
            steps {
                script {
                    sh "git config --local user.email ${GITMAIL}"
                    sh "git config --local user.name ${GITNAME}"
                    sh "git fetch origin main"
                    sh "git reset --hard origin/main"

                    // 이미지 태그 변경
                    sh "sed -i 's@image:.*@image: ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}@g' reservation.yaml"

                    // `.gitignore` 변경 방지 & 추가 파일 push 방지
                    sh "git add reservation.yaml"
                    sh "git commit -m 'Update manifest with new image tag: ${currentBuild.number}'"

                    // ✅ 원격지에서 변경된 다른 매니페스트 파일들이 있을 경우 pull & rebase
                    sh "git pull --rebase origin main || true"

                    // ✅ push 실행
                    sh "git push origin main"
                }
            }
        }
    }

    // ✅ Discord 알림 전송
    post {
        success {
            script {
                withCredentials([string(credentialsId: 'jenkins-discord-webhook', variable: 'DISCORD_URL')]) {
                    def discordMessage = """{
                        "username": "Jenkins",
                        "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                        "embeds": [{
                            "title": "✅ Jenkins Build 성공!",
                            "description": "파이프라인 빌드가 성공적으로 완료되었습니다.",
                            "color": 3066993,
                            "fields": [
                                {
                                    "name": "프로젝트",
                                    "value": "Reservation Service",
                                    "inline": true
                                },
                                {
                                    "name": "빌드 번호",
                                    "value": "${currentBuild.number}",
                                    "inline": true
                                },
                                {
                                    "name": "ECR 이미지",
                                    "value": "${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}",
                                    "inline": false
                                }
                            ],
                            "footer": {
                                "text": "Jenkins CI/CD",
                                "icon_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png"
                            },
                            "timestamp": "${new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone('UTC'))}"
                        }]
                    }"""

                    sh """
                        curl -X POST -H "Content-Type: application/json" \
                        -d '${discordMessage}' \
                        ${DISCORD_URL}
                    """
                }
            }
        }
    }
}