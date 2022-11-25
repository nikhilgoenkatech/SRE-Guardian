import sys
import json
import requests


# *******************************************************************************    
#           Function to pull execution details
# *******************************************************************************    
def pull_exec_success (DT_URL, DT_TOKEN, exec_id):
  try:
    endpoint=DT_URL + "/api/v2/synthetic/executions/"+str(exec_id)
    header={'Accept':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(DT_TOKEN)}
    config_post = requests.get(endpoint, headers=header)
    jsonObj = json.loads(config_post.text)

    state=0
    status=jsonObj["simpleResults"]["status"]

    if (status == "SUCCESS"):
     state=1

  except Exception as e:
     print("Exception in pull_exec_success " + str(e))

  finally:
    print("Succesfully completed pull_exec_success")
    return state

# *******************************************************************************    
#             Main function 
# *******************************************************************************    
if __name__ == "__main__":
   DT_URL = sys.argv[1]
   DT_TOKEN = sys.argv[2]

   state = pull_exec_success(DT_URL, DT_TOKEN, sys.argv[3])
   print(state)
   sys.exit(state)
