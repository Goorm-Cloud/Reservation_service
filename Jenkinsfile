pipeline {
    agent any
    environment {
        GITNAME = 'rttitity'
        GITMAIL = 'jinwoo25803@gmail.com'
        GITWEBADD = 'https://github.com/Goorm-Cloud/Reservation_service.git'        // 소스코드 레포지토리 주소
        GITSSHADD = 'git@github.com:Goorm-Cloud/manifast-reservation.git'                 // 매니페스트 레포지토리 주소 (https 안댐)
        GITCREDENTIAL = 'git_cre_zinucha'
        ECR_REGISTRY = '651706756261.dkr.ecr.ap-northeast-2.amazonaws.com'
        ECR_REPO = 'reservation_service'
        AWS_CREDENTIAL = 'zinucha_AWS_Credentials' // AWS 자격증명 설정 (Jenkins Credential)
        DISCORD_WEBHOOK = credentials('jenkins-discord-webhook')
    }
    stages {
        stage('Checkout Github') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
            post {
                failure {
                    sh "echo clone failed"
                }
                success {
                    sh "echo clone success"
                }
            }
        }

        // config.py .env 파일 가져오기
        stage('Create config.py & .env') {
            steps {
                script {
                    // 현재 작업 디렉토리 안에 app 디렉토리 생성
                    sh 'mkdir -p $WORKSPACE/app'

                    withCredentials([
                        string(credentialsId: 'config_secret', variable: 'CONFIG_SECRET'),
                        string(credentialsId: 'env_secret', variable: 'ENV_SECRET')
                    ]) {
                        // 환경 변수 파일 및 config.py 생성
                        sh 'echo "$CONFIG_SECRET" > $WORKSPACE/app/config.py'
                        sh 'echo "$ENV_SECRET" > $WORKSPACE/app/.env'
                    }
                }
            }
        }

        // ECR login stage
        stage('AWS ECR Login') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: AWS_CREDENTIAL]]) {
                        sh "aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    }
                }
            }
            post {
                failure {
                    sh "echo ECR login failed"
                }
                success {
                    sh "echo ECR login success"
                }
            }
        }

        // 도커 이미지 빌드 stage
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number} ."
                sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:latest ."
                // currentBuild.number 젠킨스가 제공하는 빌드넘버 변수
                // oolralra/fast:<빌드넘버> 와 같은 이미지가 만들어질 예정.

            }
            post {
                failure {
                    sh "echo image build failed"
                }
                success {
                    sh "echo image build success"
                }
            }
        }


        stage('Push Docker Image to ECR') {
            steps {
                sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:latest"
            }
            post {
                failure {
                    sh "docker image rm -f ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                    sh "docker image rm -f ${ECR_REGISTRY}/${ECR_REPO}:latest"
                    sh "echo push failed"
                    // 성공하든 실패하든 로컬에 있는 Docker image 는 삭제
                }
                success {
                    sh "docker image rm -f ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                    sh "docker image rm -f ${ECR_REGISTRY}/${ECR_REPO}:latest"
                    sh "echo push success"
                    // 성공하든 실패하든 로컬에 있는 Docker image 는 삭제

                }
            }
        }


        stage('EKS manifest file update') {
            steps {
                git credentialsId: GITCREDENTIAL, url: GITSSHADD, branch: 'main'
                sh "git config --global user.email ${GITMAIL}"
                sh "git config --global user.name ${GITNAME}"
                sh "sed -i 's@${DOCKERHUB}:.*@${DOCKERHUB}:${currentBuild.number}@g' reservation.yml"

                sh "git add ."
                sh "git branch -M main"
                sh "git commit -m 'fixed tag ${currentBuild.number}'"
                sh "git remote remove origin"
                sh "git remote add origin ${GITSSHADD}"
                sh "git push origin main"
            }
            post {
                failure {
                    sh "echo manifest update failed"
                }
                success {
                    sh "echo manifest update success"
                }
            }
        }


    }

    // 파이프라인 빌드 성공시 Discord 로 알림 메시지 전송
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
                            },
                            {
                                "name": "커밋 로그",
                                "value": "[GitHub Repository](${GITWEBADD})",
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
                    ${DISCORD_WEBHOOK}
                """
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
                                "name": "GitHub Repo",
                                "value": "[Repository Link](${GITWEBADD})",
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
                    ${DISCORD_WEBHOOK}
                """
            }
        }
    }
}