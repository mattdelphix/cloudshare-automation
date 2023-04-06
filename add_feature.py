from cloudshare_functions import *

blueprint_name_mappings = get_feature_blueprint(Feature)
vms_name_mappings = get_feature_VMs(Feature)
project_name_mappings = get_feature_project(Feature)

#Makes sure environment exist before checking content VMs
Env_data = check_if_env_exists_return_data(Env_name)

#Get Project ID from Project Name info to later get VM ID
projects = get_Projects()
for line in projects:
    if line["name"] == project_name_mappings:
        project_ID = {"id": line["id"]}

#Get Blueprint info to later get VM ID
project_info = get_allBlueprintInfo(project_ID)
for line in project_info:
    if line["name"] == blueprint_name_mappings:
        blueprint_ID = {"id": line["id"]}

#Get machines info
blueprint_details = get_BlueprintInfo(project_ID, blueprint_ID)["createFromVersions"][0]["machines"]

#Loop for number of VMS
list_of_VMS=[]
for VM_Name in vms_name_mappings:
    if check_if_VM_exists_on_Env(Env_data, VM_Name):
        for line in blueprint_details:
            if line["name"] == VM_Name:
                VMsnapshot = {"id": line["id"], "name": line["name"]}
                list_of_VMS.append([VMsnapshot, VM_Name])
                ##run_parallel(add_VM(Env_data, VMsnapshot, VM_Name, "Running", "CREATE"))
                add_VM_from_snapshot(Env_data, VMsnapshot)
                vm_execution_monitor(Env_data, VM_Name, "Running", "CREATE")

command_build = ""
#create vms in parallel
for line in list_of_VMS:
    command_build = command_build + 'add_VM(' + str(Env_data) + ', ' + str(line[0]) + ',"' + str(line[1]) + '", "Running", "CREATE"),'

whole_command = command_build[:-1]
run_parallel(whole_command)
