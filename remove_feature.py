from cloudshare_functions import *

blueprint_name_mappings = get_feature_blueprint(Feature)
vms_name_mappings = get_feature_VMs(Feature)
project_id_mappings = {"id": get_feature_project(Feature)}

#Makes sure environment exist before checking content VMs
Env_data = check_if_env_exists_return_data(Env_name)

#Get all Envs VMS information
vms_in_env = []
vms_info_env = get_env_status(Env_data)["vms"]
for x in vms_info_env:
    vms_in_env.append(x["name"])


#Loop VMS in Mappings present in Feature
for VM_Name in vms_name_mappings:
    #check if VM has dependencies
    if check_VM_has_dependencies(vms_in_env, VM_Name, Feature, vms_name_mappings):
        for x in vms_info_env:
            if x["name"] == VM_Name:
                VM = {"id": x["id"], "name": x["name"]}
                if VM is not None:
                    #remove_VM(Env_data, VM, VM_Name, "Deleted", "DELETE")
                    delete_VM(VM)
                    vm_execution_monitor(Env_data, VM_Name, "Deleted", "DELETE")
