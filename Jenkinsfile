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
    }

    stages {
        stage('Checkout Application Repository') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
        }

        // ✅ .gitignore 적용 (로컬에서만, 원격에 영향 없음)
        stage('Apply .gitignore Locally') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'gitignore_secret', variable: 'GITIGNORE_CONTENT')]) {
                        sh '''
                        echo "$GITIGNORE_CONTENT" > .gitignore
                        '''
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
        stage('Update EKS Manifest') {
            steps {
                script {
                    sh '''
                    git config --local user.email ${GITMAIL}
                    git config --local user.name ${GITNAME}
                    git fetch origin main
                    git reset --hard origin/main
                    sed -i 's@image:.*@image: ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}@g' reservation.yaml
                    git add reservation.yaml
                    git commit -m "Update manifest with new image tag: ${currentBuild.number}" || true
                    git pull --rebase --autostash origin main || true
                    git push origin main
                    '''
                }
            }
        }
    }
    // ✅ 빌드 성공 시 Discord 알림
    post {
        success {
            script {
                withCredentials([string(credentialsId: 'jenkins-discord-webhook', variable: 'DISCORD_URL')]) {
                    sh '''
                    curl -X POST -H "Content-Type: application/json" \
                    -d '{
                        "username": "Jenkins",
                        "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                        "embeds": [{
                            "title": "✅ Jenkins Build 성공!",
                            "description": "파이프라인 빌드가 성공적으로 완료되었습니다.",
                            "color": 3066993,
                            "fields": [
                                {"name": "프로젝트", "value": "Reservation Service", "inline": true},
                                {"name": "빌드 번호", "value": "'${currentBuild.number}'", "inline": true},
                                {"name": "ECR 이미지", "value": "'${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}'", "inline": false}
                            ],
                            "footer": {
                                "text": "Jenkins CI/CD",
                                "icon_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png"
                            },
                            "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
                        }]
                    }' ${DISCORD_URL}
                    '''
                }
            }
        }

        failure {
            script {
                sh "echo 'Jenkins Pipeline Failed ❌'"
            }
        }
    }
}