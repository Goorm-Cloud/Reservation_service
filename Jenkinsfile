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
        // ✅ 애플리케이션 소스코드 체크아웃
        stage('Checkout Application Repository') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
                userRemoteConfigs: [[credentialsId: GITCREDENTIAL, url: GITWEBADD]]])
            }
        }

        // ✅ .gitignore 파일 적용 (Secret Text)
        stage('Apply .gitignore from Credentials') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'gitignore_secret', variable: 'GITIGNORE_CONTENT')]) {
                        sh 'echo "$GITIGNORE_CONTENT" > .gitignore'
                        sh 'git rm --cached .gitignore || true'  // 기존 Git 추적 해제
                        sh 'git update-index --assume-unchanged .gitignore'
                    }
                }
            }
        }

        // ✅ config.py & .env 파일 생성 (Secret File 활용)
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

        // ✅ AWS ECR 로그인
        stage('AWS ECR Login') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: AWS_CREDENTIAL]]) {
                        sh "aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    }
                }
            }
        }

        // ✅ Docker 이미지 빌드 및 푸시
        stage('Build & Push Docker Image') {
            steps {
                script {
                    sh "docker build -t ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number} ."
                    sh "docker push ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}"
                }
            }
        }

        // ✅ 보안 강화를 위해 config.py & .env 삭제
        stage('Cleanup Sensitive Files') {
            steps {
                sh "rm -f config.py .env"
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

        // ✅ 매니페스트 파일 업데이트 (이미지 태그 변경)
        stage('Update EKS Manifest') {
            steps {
                script {
                    sh "git config --local user.email ${GITMAIL}"
                    sh "git config --local user.name ${GITNAME}"
                    sh "git fetch origin main"
                    sh "git reset --hard origin/main"

                    // ✅ 이미지 태그 변경
                    sh "sed -i 's@image:.*@image: ${ECR_REGISTRY}/${ECR_REPO}:${currentBuild.number}@g' reservation.yaml"

                    // ✅ 변경 사항 커밋 (자동 충돌 해결 & rebase 적용)
                    sh "git add reservation.yaml"
                    sh "git commit -m 'Update manifest with new image tag: ${currentBuild.number}' || echo 'No changes to commit'"
                    sh "git pull --rebase --autostash origin main || true"
                    sh "git push origin main"
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