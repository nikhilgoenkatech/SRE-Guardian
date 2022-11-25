node {
    environment {
        APP_NAME = "SampleNodeJs"
        STAGING = "Staging"
        PRODUCTION = "Production"
    }
    echo "1 ${EXECUTION_ID}" 
    
    stage('Checkout') {
        // Checkout our application source code
        git url: 'https://github.com/nikhilgoenkatech/JenkinsBankApp.git'
    }

    stage('Build') {
        // Lets build our docker image
        dir ('sample-bank-app-service') {
            try {
                env.DOCKERFILE = env.DOCKERFILE
            }
            catch (e) {
            //catch (groovy.lang.MissingPropertyException e ) {
                echo "Received an exception!!!"
                env.DOCKERFILE = "Dockerfile"
            }
            def app = docker.build("sample-bankapp-service:${BUILD_NUMBER}", "-f ${env.DOCKERFILE} .")
        }
    }
    
    stage('CleanStaging') {
        // The cleanup script makes sure no previous docker staging containers run
        sh 'docker ps -f name=SampleOnlineBankStaging -q | xargs --no-run-if-empty docker container stop'
        sh 'docker container ls -a -fname=SampleOnlineBankStaging -q | xargs -r docker container rm'
    }
    
    stage('DeployStaging') {
        // Lets deploy the previously build container
        def app = docker.image("sample-bankapp-service:${BUILD_NUMBER}")
        app.run("--network mynetwork --name SampleOnlineBankStaging -p 3000:3000 " +
                "-e 'DT_CLUSTER_ID=SampleOnlineBankStaging' " + 
                "-e 'DT_TAGS=Environment=Staging Service=Sample-NodeJs-Service' " +
                "-e 'DT_CUSTOM_PROP=ENVIRONMENT=Staging JOB_NAME=${JOB_NAME} " + 
                    "BUILD_TAG=${BUILD_TAG} BUILD_NUMBER=${BUIlD_NUMBER}'")

        dir ('dynatrace-scripts') {
            // push a deployment event on the host with the tag JenkinsInstance created using automatic tagging rule
            sh './pushdeployment.sh HOST CONTEXTLESS JenkinsInstance ' +
               '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' + 
               'Jenkins ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
            
            // now I push one on the actual service (it has the tags from our rules)
            sh './pushdeployment.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankStaging ' + 
               '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} ' + 
               'Jenkins ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
            
            // Create a on-demand synthetic monitor so as to check the UI functionlity
            sh './synthetic-monitor.sh Staging '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' 3000'
            
            // Create a sample dashboard for the staging stage
            sh './create-dashboard.sh Staging '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' DockerService SampleOnlineBankStaging'
        }
    }
    
    stage('Testing') {
        // lets push an event to dynatrace that indicates that we START a load test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankStaging ' +
               '"STARTING Load Test" ${JOB_NAME} "Starting a Load Test as part of the Testing stage"' + 
               ' ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }
        dir('dynatrace-scripts') {
            // Trigger the on-demand synthetic monitor as part of the Testing cycle
            ${EXECUTION_ID} = sh('python3 trigger_syn_monitor.py ${DT_URL} ${DT_TOKEN} ${BUILD_NUMBER}')
        }
        
        // lets run some test scripts
        dir ('sample-bank-app-service-tests') {
            // start load test - simulating traffic for Staging enviornment on port 3000 

            sh "rm -f stagingloadtest.log stagingloadtestcontrol.txt"
            sh "python3 smoke-test.py 3000 10 ${BUILD_NUMBER} stagingloadtest.log ${PUBLIC_IP} SampleOnlineBankStaging"
            archiveArtifacts artifacts: 'stagingloadtest.log', fingerprint: true
        }

        // lets push an event to dynatrace that indicates that we STOP a load test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankStaging '+
               '"STOPPING Load Test" ${JOB_NAME} "Stopping a Load Test as part of the Testing stage" '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }

        // lets push an event to dynatrace that indicates that we START a sanity test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankStaging ' +
               '"STARTING Sanity-Test" ${JOB_NAME} "Starting Sanity-test of the Testing stage"' + 
               ' ${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }
        
        // lets run some test scripts
        dir ('sample-bank-app-service-tests') {
            // start load test - simulating traffic for Staging enviornment on port 3000 

            sh "rm -f stagingloadtest.log stagingloadtestcontrol.txt"
            sh "python3 sanity-test.py 3000 10 ${BUILD_NUMBER} stagingsanitytest.log ${PUBLIC_IP} SampleOnlineBankStaging"
            archiveArtifacts artifacts: 'stagingsanitytest.log', fingerprint: true
        }

        // lets push an event to dynatrace that indicates that we STOP a load test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankStaging '+
               '"STOPPING Sanity Test" ${JOB_NAME} "Stopping Sanity-test of the Testing stage" '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }
    }
    
    stage('ValidateStaging') {
        dir ('dynatrace-scripts') {      
            try {
                 // Check if there are vulnerabilities identified by DT
                 DYNATRACE_SEC_PROBLEM_COUNT = 0
                 def DYNATRACE_SEC_PROBLEM_COUNT = sh(returnStatus: true, script: 'python3 checkforvulnerability.py ${DT_URL} ${DT_TOKEN} [Environment]Environment:Staging 7.5')
                 echo 'Printing the returned problem count'
                 echo "$DYNATRACE_SEC_PROBLEM_COUNT"
                
                 if (DYNATRACE_SEC_PROBLEM_COUNT) {
                    error("Dynatrace identified some vulnerabilities. ABORTING the build!!")
                 }
            } catch (e) {
                if (DYNATRACE_SEC_PROBLEM_COUNT) {
                    sh 'mv securityVulnerabilityReport.txt securityVulnerabilityReportStaging.txt'
                    archiveArtifacts artifacts: 'securityVulnerabilityReportStaging.txt', fingerprint: true
                    currentBuild.result = 'ABORTED'
                }
                throw(e)
            }
            archiveArtifacts artifacts: 'securityVulnerabilityReport.txt', fingerprint: true
        
            // Validate if synthetic monitor ran into any issues 
            echo "Checking Sythetic monitor status"
            try {
              STATUS = 0
                STATUS = sh 'python3 check_synthetic_run.py ${DT_URL} ${DT_TOKEN} ${EXECUTION_ID}'
            } catch (Exception e) {
                if (STATUS) {
                    error("Synthetic monitor has failed. Aboritig the build!!")
                    currentBuild.result = 'ABORTED'
                    sh "exit ${STATUS}"
                }
            }
            
            echo "Will look for any open problems"            
            // lets see if Dynatrace AI found problems -> if so - we can stop the pipeline!
            try {
                 DYNATRACE_PROBLEM_COUNT = 0
                 DYNATRACE_PROBLEM_COUNT = sh 'python3 checkforproblems.py ${DT_URL} ${DT_TOKEN} DockerService:SampleOnlineBankStaging'
            } catch (Exception e) {
                if (DYNATRACE_PROBLEM_COUNT) {
                   error("Dynatrace opened some problem. ABORTING the build!!")
                   currentBuild.result = 'ABORTED'
                   sh "exit ${DYNATRACE_PROBLEM_COUNT}"                 
               }
            }
        }
        
        // now lets generate a report using our CLI and lets generate some direct links back to dynatrace
        dir ('dynatrace-scripts') {
            sh 'python3 make_api_call.py ${DT_URL} ${DT_TOKEN} DockerService:SampleOnlineBankStaging '+
                        'service.responsetime'
            sh 'mv Test_report.csv Test_report_staging.csv'
            archiveArtifacts artifacts: 'Test_report_staging.csv', fingerprint: true
        }
    }
    
    stage('DeployProduction') {
         // first we clean production        
        sh 'docker ps -f name=SampleOnlineBankProduction -q | xargs --no-run-if-empty docker container stop'
        sh 'docker container ls -a -fname=SampleOnlineBankProduction -q | xargs -r docker container rm'

        dir ('sample-bank-app-service') {
            // now we deploy the new container
           def app = docker.build("sample-bankapp-service:${BUILD_NUMBER}", "-f ${env.DOCKERFILE} .")
           app.run("--network mynetwork --name SampleOnlineBankProduction -p 3010:3000 "+
                "-e 'DT_CLUSTER_ID=SampleOnlineBankProduction' "+
                "-e 'DT_TAGS=Environment=Production Service=Sample-NodeJs-Service' "+
                "-e 'DT_CUSTOM_PROP=ENVIRONMENT=Production JOB_NAME=${JOB_NAME} "+
                    "BUILD_TAG=${BUILD_TAG} BUILD_NUMBER=${BUIlD_NUMBER}'")
        }
        
        dir ('dynatrace-scripts') {
            // push a deployment event on the host with the tag JenkinsInstance:
            sh './pushdeployment.sh HOST CONTEXTLESS JenkinsInstance "Ken-securityGroup-11, LevelUPSecurityGroup"' +
               '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} Jenkins '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
            
            // now I push one on the actual service (it has the tags from our rules)
            sh './pushdeployment.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankProduction '+
               '${BUILD_TAG} ${BUILD_NUMBER} ${JOB_NAME} Jenkins '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'

            // Create a sample synthetic monitor so as to check the UI functionlity
           sh './synthetic-monitor.sh Production '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' 3010'
            
          // Create a sample dashboard for the staging stage
          sh './create-dashboard.sh Production '+  '${JOB_NAME} ${BUILD_NUMBER}' + ' DockerService SampleOnlineBankProduction'    
            
        }        
    }    
    
    stage('WarmUpProduction') {
        // lets push an event to dynatrace that indicates that we START a load test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankProduction '+
               '"STARTING Load Test" ${JOB_NAME} "Starting a Load Test to warm up new prod deployment" '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }
        
        // lets run some test scripts
        dir ('sample-bank-app-service-tests') {
            // start load test and run for 120 seconds - simulating traffic for Production enviornment on port 3010 
            sh "rm -f productionloadtest.log productionloadtestcontrol.txt"
            sh "python3 smoke-test.py 3010 10 ${BUILD_NUMBER} productionloadtest.log ${PUBLIC_IP} SampleOnlineBankProduction "
            archiveArtifacts artifacts: 'productionloadtest.log', fingerprint: true
        }

        // lets push an event to dynatrace that indicates that we STOP a load test
        dir ('dynatrace-scripts') {
            sh './pushevent.sh SERVICE CONTEXTLESS DockerService SampleOnlineBankProduction '+
               '"STOPPING Load Test" ${JOB_NAME} "Stopping a Load Test as part of the Production warm up phase" '+
               '${JENKINS_URL} ${JOB_URL} ${BUILD_URL} ${GIT_COMMIT}'
        }
    }
    
    stage('ValidateProduction') {
        dir ('dynatrace-scripts') {      
            try {
                 // Check if there are vulnerabilities identified by DT
                 DYNATRACE_SEC_PROBLEM_COUNT = 0
                 def DYNATRACE_SEC_PROBLEM_COUNT = sh(returnStatus: true, script: 'python3 checkforvulnerability.py ${DT_URL} ${DT_TOKEN} [Environment]Environment:Staging 9.5')
                 echo 'Printing the returned problem count'
                 echo "$DYNATRACE_SEC_PROBLEM_COUNT"
                
                 if (DYNATRACE_SEC_PROBLEM_COUNT) {
                    error("Dynatrace identified some vulnerabilities. ABORTING the build!!")
                 }
            } catch (e) {
                if (DYNATRACE_SEC_PROBLEM_COUNT) {
                    sh 'mv securityVulnerabilityReport.txt securityVulnerabilityReportProd.txt'
                    archiveArtifacts artifacts: 'securityVulnerabilityReportProd.txt', fingerprint: true
                    currentBuild.result = 'ABORTED'
                }
                throw(e)
            }

            // lets see if Dynatrace AI found problems -> if so - we can stop the pipeline!
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
        
        // now lets generate a report using our CLI and lets generate some direct links back to dynatrace
        dir ('dynatrace-scripts') {
            sh 'python3 make_api_call.py ${DT_URL} ${DT_TOKEN} DockerService:SampleOnlineBankProduction '+
                        'service.responsetime'
            sh 'mv Test_report.csv Test_report_prod.csv'
            archiveArtifacts artifacts: 'Test_report_prod.csv', fingerprint: true
        }
    }    
}
