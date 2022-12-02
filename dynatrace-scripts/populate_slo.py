import sys
import json
import requests

###

#####################################################################################
##                 Function to create SLOs - Response Time and Failure Rate
#######################################################################################
def get_slo_id(DT_URL, DT_TOKEN, endpoint):
  try:
    slo_id = ""  
    query = str(DT_URL) + endpoint 
    #print(query)

    get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(DT_TOKEN)}
    populate_data = requests.get(query, headers = get_param)
    #print(populate_data.status_code)

    data = populate_data.json()
    #print(data)
    slo_id = data["slo"][0]["id"]

  except Exception as e:
    print("Received an exception in get_slo_id", str(e)) 

  finally:
    return slo_id  

#####################################################################################
##                 Function to create SLOs - Response Time and Failure Rate
#######################################################################################
def get_slo_details(DT_URL, DT_TOKEN):
  try:
    #Get Service SLOs  
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20Response Time SLO%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    response_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20Failure%20Rate%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    failure_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)

    #Get DB SLOs 
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20DB Response Time SLO%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    db_response_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20Database Failure%20Rate%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    db_failure_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)

    #Get APP SLOs 
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20App Response Time SLO%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    app_response_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)
    endpoint = "/api/v2/slo?sloSelector=name%28%22" + sys.argv[3] + "%20-%20App Failure%20Rate%22%29&sort=name&timeFrame=CURRENT&demo=false&evaluate=false&enabledSlos=true&showGlobalSlos=true"
    app_failure_slo_id = get_slo_id(DT_URL,DT_TOKEN,endpoint)

  except Exception as e:
    print("Received an exception in get_slo_details", str(e)) 

  finally:
    return response_slo_id, failure_slo_id, db_response_slo_id, db_failure_slo_id, app_response_slo_id, app_failure_slo_id 

#######################################################################################
##                    Function main
#######################################################################################
if __name__ == "__main__":
  try:
     DT_URL = sys.argv[1]
     DT_TOKEN = sys.argv[2]

     response_slo_id, failure_slo_id, db_response_slo_id, db_failure_slo_id, app_response_slo_id, app_failure_slo_id = get_slo_details(DT_URL, DT_TOKEN)

     #Create dashboard
     import subprocess
     subprocess.call(["sh","./create-dashboard.sh",DT_URL,DT_TOKEN,sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7]])
    
     #DASHBOARD_PAYLOAD["dashboardMetadata"]["name"] = sys.argv[4] + sys.argv[5] + ":" + sys.argv[6]
     #for tile in DASHBOARD_PAYLOAD["tiles"]:
     #  #Replace the slo tiles with the id of slos  
     #  if DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "response_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = response_slo_id
     #  elif DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "db_response_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = db_response_slo_id
     #  elif DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "app_response_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = app_response_slo_id

     #  elif DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "failure_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = failure_slo_id 
     #  elif DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "db_failure_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = db_failure_slo_id 
     #  elif DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = "app_failure_slo_id":
     #    DASHBOARD_PAYLOAD["tiles"][tile]["assignedEntities"] = app_failure_slo_id 
     # 
     #  DASHBOARD_PAYLOAD 
     #  DASHBOARD_PAYLOAD["tiles"][4]["name"]["filtersPerEntityType"]["AUTO_TAGS"][0] = "\"" + sys.argv[7] + sys.argv[3] + "\""
     #json = DASHBOARD_PAYLOAD.replace("$1",sys.argv[4]).replace("$2",sys.argv[5]).replace("$3",sys.argv[6]).replace("$4",sys.argv[7]).replace("$5",sys.argv[3])
     #json_obj = json_obj.replace("response_slo_id",str(response_slo_id)).replace("db_response_slo_id",str(db_response_slo_id)).replace("app_response_slo_id",str(app_response_slo_id))
     #json_obj = json_obj.replace("failure_slo_id",str(failure_slo_id)).replace("db_failure_slo_id",str(db_failure_slo_id)).replace("app_failure_slo_id",str(app_failure_slo_id))


     #query = str(DT_URL) + "/api/config/v1/dashboards/"
     #post_param = {'Content-Type':'application/json', 'Authorization':'Api-Token {}'.format(DT_TOKEN)}
     #populate_data = requests.post(query, headers = post_param, data = json.dumps(json_obj))

     #print(json.dumps(json_str))
     #print(populate_data.status_code)
  except Exception as e:
    print("Exception in main " + str(e))

  finally:
    print("Succesfully completed main")
    #sys.exit(response_slo_id, failure_slo_id, db_response_slo_id, db_failure_slo_id, app_response_slo_id, app_failure_slo_id)
