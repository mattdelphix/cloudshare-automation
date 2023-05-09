import sys
import cloudshare
import configparser
import json
import time
import argparse
import os


def request(method, path, queryParams=None, content=None):
    res = cloudshare.req(hostname="use.cloudshare.com",
                         method=method,
                         apiId=API_ID,
                         apiKey=API_KEY,
                         path=path,
                         queryParams=queryParams,
                         content=content)
    if res.status // 100 != 2:
        raise Exception('{} {}'.format(res.status, res.content['message']))
    return res.content


def get(path, queryParams=None):
    return request('GET', path, queryParams=queryParams)


def post(path, content=None):
    return request('POST', path, content=content)


def put(path, queryParams=None, content=None):
    return request('PUT', path, queryParams=queryParams, content=content)


def delete(path, queryParams=None):
    return request('DELETE', path, queryParams=queryParams)


def get_env_id():
    return get('envs')


def get_env_status(env):
    return get('/envs/actions/getextended?envId=' + env['id'])


def get_getVMtemplates():
    return get('/templates', None)


def get_SnapshotInfo(snapshot):
    return get('/snapshots/' + snapshot['id'], {'snapshotId': snapshot['id']})


def get_allSnapshotsInfo(env):
    return get('/snapshots/actions/getforenv', {'envId': env['id']})


def get_allBlueprintInfo(project):
    return get("/projects/" + project["id"] + "/blueprints", {'projectId': project['id']})


def get_BlueprintInfo(project, blueprint):
    return get("/projects/" + project["id"] + "/blueprints/" + blueprint['id'],
               {'projectId': project['id'], "blueprintId": blueprint['id']})


def get_Projects():
    return get('/projects', None)


def get_Policies(project):
    return get('/projects/' + project["id"] + "/policies/", None)


def get_Region():
    return get('/regions', None)

def get_Team():
    return get('/teams', None)

def add_env(name,description, project, policy, region, ownerEmail, team, blueprint, snapshot):
    return post("/envs/", {
        "environment": {
            "name": name,
            "description": description,
            "projectId": project["id"],
            "policyId": policy["id"],
            "regionId": region["id"],
            "ownerEmail": ownerEmail,
            "teamId": team["id"]
        },
        "itemsCart": [
            {
                "type": 1,
                "blueprintId": blueprint["id"],
                "snapshotId": snapshot["id"]
            }
        ]
    })


def resume_env(env):
    return put("/envs/actions/resume", {'envId': env['id']})


def suspend_env(env):
    return put("/envs/actions/suspend", {'envId': env['id']})


def extend_env(env):
    return put("/envs/actions/extend", {'envId': env['id']})


def remove_env(env):
    return delete("/envs/ID", {'ID': env['id']})


def delete_VM(machine):
    return delete("/vms", {'ID': machine['id']})

def add_VM_from_snapshot(env, machine):
    return put("/envs", None, {
        "envId": env['id'],
        "itemsCart": [
            {
                "type": "4",
                "name": machine['name'],
                "description": " ",
                "machineId": machine['id'],
                "disconnectedFromNetworks": "false"
            }
        ]
    })

def add_VM(env,machine,vm_name, status_text, text):
    add_VM_from_snapshot(env, machine)
    vm_execution_monitor(env, vm_name, status_text, text)
    return


def remove_VM(env, machine, vm_name, status_text, text):
    delete_VM(machine)
    vm_execution_monitor(env, vm_name, status_text, text)
    return

def execute_command_vm (machine, path):
    return post("/vms/actions/executepath", None, {
        "vmID": machine['id'],
        "path": path
    })


def execute_command (machine, path):
    execution = execute_command_vm(machine, path)
    exit_code = 99
    while exit_code != 0:
        exit_code = get_script_execution_status(machine, execution)["exit_code"]
        time.sleep(10)

    print("Command ", path, " running on VM ", machine["name"], " has completed!")



def get_script_execution_status(machine, execution):
    print("polling execution status...")
    return get("vms/actions/checkExecutionStatus", {
        'vmId': machine['id'],
        'executionId': execution['executionId']
    })


def vm_execution_monitor(env, vm_name, status_text, text):
    # VM Status text values as there is not code.
    # No code values known "Loading from Snapshot" / "Running"
    flag_vm_exists = False
    status_vm = None
    print("Waiting for order to ", text, " complete for VM ", vm_name)
    while status_vm != status_text:
        time.sleep(30)
        flag_vm_exists = False
        res = get_env_status(env)["vms"]
        for x in res:
            if x["name"] == vm_name:
                # print(x["statusText"],  status_vm, x["progress"])
                if x["statusText"] != status_text:
                    status_vm = x["statusText"]
                    flag_vm_exists = True
                else:
                    print("VM ", vm_name, " is ready!")
                    return
        if not flag_vm_exists:
            print("VM -", vm_name, "- not found in the catalog")
            return


##Needs testing
def env_execution_monitor(env, status_text, text):
    # 2: Ready
    # 3: Suspended
    # 4: Archived
    # 5: Deleted
    # 7: Taking a Snapshot
    # 8: Preparing
    # 9: Creation Failed
    status_env = None
    env_name = env["name"]
    print("Waiting for order to ", text, " to complete for Environment ", env_name)
    while status_env != status_text:
        time.sleep(30)
        res = get_env_status(env)
        if res["name"] == env_name:
            status_env = res["statusText"]
            if status_env == "Creation Failed":
                print("Environment creation failed!")
                break

    print("Action of ", text, " for new Environment ", env_name, " is completed! ")



def read_generic_config(filename=None):
    current_dir = os.path.dirname(__file__)
    if filename is None:
        configFile = current_dir + "/cloudshare_config.conf"
    else:
        configFile = current_dir + "/" + filename
    configParser = configparser.RawConfigParser(allow_no_value=False)
    configParser.read(configFile)
    return configParser


def read_mappings_config(filename=None):
    current_dir = os.path.dirname(__file__)
    if filename is None:
        mappinggFile = current_dir + "/mapping.json"
    else:
        mappinggFile = current_dir + "/" + filename
    f = open(mappinggFile)
    return json.load(f)


def check_feature_exists(text):
    flag = 0
    for x in mappings["Features"]:
        if x["FeatureName"] == text:
            return 1
    return 0


def get_feature_blueprint(feature_name):
    for x in mappings["Features"]:
        if x["FeatureName"] == feature_name:
            return x["FeatureDetails"]["Blueprint"]


def get_feature_VMs(feature_name):
    for x in mappings["Features"]:
        if x["FeatureName"] == feature_name:
            return x["FeatureDetails"]["RequiredVM"]


def get_feature_project(feature_name):
    for x in mappings["Features"]:
        if x["FeatureName"] == feature_name:
            return x["FeatureDetails"]["ProjectName"]


def check_if_env_exists_return_data(environemnt_name):
    # check if environemnt exists  before looking for VMs
    flag = 0
    res = get_env_id()
    for x in res:
        if x["name"] == environemnt_name:
            flag = 1
            env = {"id": x["id"], "name": x["name"]}

    if flag == 0:
        print("Environment ", environemnt_name, " not found, exiting...")
        sys.exit(1)
    print("Working on Environment ", environemnt_name, "!!!")
    return env


def check_if_VM_exists_on_Env(env, vm_name):
    # check for existing VMS
    res = get_env_status(env)["vms"]
    for x in res:
        if x["name"] == vm_name:
            print("VM ", x["name"], " exists for this Environment ", env["name"], ", skipping...")
            return 0
    return 1


def check_VM_has_dependencies(env_vms_list, vm_name, feature, vms_in_mappings):
    if vm_name in env_vms_list:
        for x in mappings["Dependencies"]:
            if feature in x["FeatureDependency"]:
                if vm_name == x["VMName"]:
                    # Get total of dependencies minus the ones we want to remove
                    collateral_dependency = set(list(set(x["VMDependantVMs"]) - set(vms_in_mappings)))
                    # Do these exist in the current env ?
                    # if not set(collateral_dependency).issubset(set(env_vms_list)):
                    if not any(x in collateral_dependency for x in env_vms_list):
                        print("VM -", vm_name, "- exists and does not have dependencies")
                        return 1
                    else:
                        print("Skipping VM -", vm_name, "- because of dependencies with VMs ", collateral_dependency)
                        return 0
                else:
                    return 1
            else:
                return 1
    else:
        print("VM -", vm_name, "- present on Feature does not exist for this environment, skipping...")
        return 0


""" def run_parallel(*functions):
    '''
    Run functions in parallel
    '''
    from multiprocessing import Process
    processes = []
    for function in functions:
        proc = Process(target=function)
        proc.start()
        processes.append(proc)
    for proc in processes:
        proc.join()
"""

# Get Generic values
configuration = read_generic_config()
mappings = read_mappings_config()
try:
    API_ID = configuration.get('Generic_config', 'API_ID')
    if not API_ID:
        print("Parameter API_ID seems to be empty...")
        sys.exit(1)
    API_KEY = configuration.get('Generic_config', 'API_KEY')
    if not API_KEY:
        print("Parameter API_KEY seems to be empty...")
        sys.exit(1)
    ENV_NAME = configuration.get('Generic_config', 'ENV_NAME')
    if not ENV_NAME:
        print("Parameter ENV_NAME seems to be empty...")
        sys.exit(1)
    version = configuration.get('Generic_config', 'version')
    if not version:
        print("Parameter version seems to be empty...")
        sys.exit(1)
except:
    print("An exception occurred while reading the configuration file 'cloudshare_config.conf' please confirm file exists and has all fields, exiting...")
    sys.exit(1)

