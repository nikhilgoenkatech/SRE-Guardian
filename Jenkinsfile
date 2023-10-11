node {
    // Define the log file path
    def logFilePath = "${WORKSPACE}/jenkins-log.txt"

    try {
        // Use tee to capture the entire build output to the log file
        sh "exec > >(tee ${logFilePath})"
        sh "exec 2>&1"
        
        stage('Checkout') {
            git url: 'https://github.com/nikhilgoenkatech/SRE-Guardian.git'
        }

        stage('Build') {
            dir('sample-bank-app-service') {
                // You can capture the output of this stage if needed
                def app = docker.build("sample-bankapp-service:${BUILD_NUMBER}", "-f Dockerfile .")
            }
        }
        
        stage('CleanStaging') {
            dir('sample-bank-app-service') {
                sh 'docker ps -f name=SampleOnlineBankStaging -q | xargs --no-run-if-empty docker container stop'
                sh 'docker container ls -a -fname=SampleOnlineBankStaging -q | xargs -r docker container rm'
            }
        }

        stage('DeployStaging') {
            def app = docker.image("sample-bankapp-service:${BUILD_NUMBER}")
            app.run("--network mynetwork --name SampleOnlineBankStaging -p 3000:3000 " +
                    "-e 'DT_CLUSTER_ID=SampleOnlineBankStaging' " + 
                    "-e 'DT_TAGS=Environment=Staging Service=Sample-NodeJs-Service' " +
                    "-e 'DT_CUSTOM_PROP=ENVIRONMENT=Staging JOB_NAME=${JOB_NAME} " + 
                        "BUILD_TAG=${BUILD_TAG} BUILD_NUMBER=${BUILD_NUMBER}' " +
                    "-e 'RELEASE_VERSION=${BUILD_NUMBER}' " + "-e 'RELEASE_STAGE=Staging'")

            dir ('dynatrace-scripts') {
                sh './pushdeployment.sh HOST JenkinsInstance ' +
                    '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' + 
                    'Staging SampleOnlineBankStaging'

                sh './pushdeployment.sh PROCESS_GROUP_INSTANCE [Environment]Environment:Staging ' +
                    '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' + 
                    'Staging SampleOnlineBankStaging'

                sh './synthetic-monitor.sh Staging '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' 3000'

                sh "python3 create_slo.py ${DT_URL} ${DT_TOKEN} SampleOnlineBankStaging DockerService staging"

                sh "python3 populate_slo.py ${DT_URL} ${DT_TOKEN} SampleOnlineBankStaging ${JOB_NAME} staging ${BUILD_NUMBER} DockerService"
            }
        }
        
        stage('Testing') {
            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankStaging ' +
                    '"Starting a Load Test as part of Staging" ${JOB_NAME} "Starting a Load Test as part of Staging"' + 
                    ' ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }
            dir('dynatrace-scripts') {
                env.execution_id = sh(script: 'python3 trigger_syn_monitor.py ${DT_URL} ${DT_TOKEN} Staging ${BUILD_NUMBER}', returnStatus: true)
            }

            dir ('sample-bank-app-service-tests') {
                sh "rm -f stagingloadtest.log stagingloadtestcontrol.txt"
                sh "python3 smoke-test.py 3000 100 ${BUILD_NUMBER} stagingloadtest.log ${PUBLIC_IP} SampleOnlineBankStaging"
                archiveArtifacts artifacts: 'stagingloadtest.log', fingerprint: true
            }

            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankStaging '+
                    '"Stopping Load Test that started as part of the Staging." ${JOB_NAME} "Stopping a Load Test as part of the Testing stage" '+
                    '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }

            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankStaging ' +
                    '"STARTING Sanity-Test" ${JOB_NAME} "Starting Sanity-test of the Testing stage"' + 
                    ' ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }

            dir ('sample-bank-app-service-tests') {
                sh "rm -f stagingloadtest.log stagingloadtestcontrol.txt"
                sh "python3 sanity-test.py 3000 10 ${BUILD_NUMBER} stagingsanitytest.log ${PUBLIC_IP} SampleOnlineBankStaging"
                archiveArtifacts artifacts: 'stagingsanitytest.log', fingerprint: true
            }

            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankStaging '+
                    '"STOPPING Sanity Test" ${JOB_NAME} "Stopping Sanity-test of the Testing stage" '+
                    '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }
        }
        
        stage('ValidateStaging') {
            script {
                def startTime = System.currentTimeMillis()
                while (1) {        
                    try {
                        env.PROMOTION_DECISION = input message: "Approve release?", ok: "approve"
                        echo 'Received the input from user "$(env.PROMOTION_DECISION)"'
                        break
                    } catch (Exception e) {
                        sh 'echo "SRE-Guardian has disapproved the build, will not promote to production."' 
                        error("SRE-Guardian has disapproved the build, will not promote to production")
                        currentBuild.result = 'ABORTED'
                    }                     
                }    
            }
        }            
        
        stage('DeployProduction') {
            sh 'docker ps -f name=SampleOnlineBankProduction -q | xargs --no-run-if-empty docker container stop'
            sh 'docker container ls -a -fname=SampleOnlineBankProduction -q | xargs -r docker container rm'

            dir ('sample-bank-app-service') {
                def app = docker.build("sample-bankapp-service:${BUILD_NUMBER}", "-f ${env.DOCKERFILE} .")
                app.run("--network mynetwork --name SampleOnlineBankProduction -p 3010:3000 "+
                    "-e 'DT_CLUSTER_ID=SampleOnlineBankProduction' "+
                    "-e 'DT_TAGS=Environment=Production Service=Sample-NodeJs-Service' "+
                    "-e 'DT_CUSTOM_PROP=ENVIRONMENT=Production JOB_NAME=${JOB_NAME} "+
                        "BUILD_TAG=${BUILD_TAG} BUILD_NUMBER=${BUIlD_NUMBER}' " +
                    "-e 'RELEASE_VERSION=${BUILD_NUMBER}' " + "-e 'RELEASE_STAGE=Production'")
            }
            
            dir ('dynatrace-scripts') {
                sh './pushdeployment.sh HOST JenkinsInstance ' +
                    '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' +
                    'Production SampleOnlineBankProduction'

                sh './pushdeployment.sh PROCESS_GROUP_INSTANCE [Environment]Environment:Production ' +
                    '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' + 
                    'Production SampleOnlineBankProduction'

                sh './synthetic-monitor.sh Production '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' 3010'

                sh "python3 create_slo.py ${DT_URL} ${DT_TOKEN} SampleOnlineBankProduction DockerService prod"
                            
              // Create a sample dashboard for the staging stage
                sh "python3 populate_slo.py ${DT_URL} ${DT_TOKEN} SampleOnlineBankProduction ${JOB_NAME} prod ${BUILD_NUMBER} DockerService"            
            }
        } 
        
        stage('WarmUpProduction') {
            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankProduction '+
                    '"Starting a Load Test to warm up new Production Deployment." ${JOB_NAME} "Starting a Load Test to warm up new prod deployment" '+
                    '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }
            
            dir ('sample-bank-app-service-tests') {
                sh "rm -f productionloadtest.log productionloadtestcontrol.txt"
                sh "python3 smoke-test.py 3010 10 ${BUILD_NUMBER} productionloadtest.log ${PUBLIC_IP} SampleOnlineBankProduction "
                archiveArtifacts artifacts: 'productionloadtest.log', fingerprint: true
            }

            dir ('dynatrace-scripts') {
                sh './pushevent.sh SERVICE DockerService SampleOnlineBankProduction '+
                    '"STOPPING Load Test Production Deployment." ${JOB_NAME} "Stopping a Load Test as part of the Production warm up phase" '+
                    '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT} ${BUILD_NUMBER}'
            }
        }
        
        stage('ValidateProduction') {
            dir ('dynatrace-scripts') {      
                try {
                    DYNATRACE_PROBLEM_COUNT = 0
                    DYNATRACE_PROBLEM_COUNT = sh 'python3 checkforproblems.py ${DT_URL} ${DT_TOKEN} DockerService:SampleOnlineBankProduction'
                } catch (Exception e) {
                    if (DYNATRACE_PROBLEM_COUNT) {
                       error("Dynatrace opened some problem. ABORTING the build!!")
                       currentBuild.result = 'ABORTED'
                       sh "exit ${DYNATRACE_PROBLEM_COUNT}"                 
                   }
                }
            }
            
            dir ('dynatrace-scripts') {
                sh 'python3 make_api_call.py ${DT_URL} ${DT_TOKEN} DockerService:SampleOnlineBankProduction '+
                            'service.responsetime'
                sh 'mv Test_report.csv Test_report_prod.csv'
                archiveArtifacts artifacts: 'Test_report_prod.csv', fingerprint: true
            }
        }    
    } finally {
        sh "exec > /dev/null"
        sh "exec 2>&1"
    }
    
    // Archive the log file
    archiveArtifacts artifacts: 'jenkins-log.txt', allowEmptyArchive: true, onlyIfSuccessful: true
}
