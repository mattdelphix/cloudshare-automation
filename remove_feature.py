from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--available_features", action="version", version="List all available Features: " + get_features())
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--feature", type=str, required=True, help="Feature to remove")
parser.add_argument("--email", type=str, required=True, help="Email of requestor")
args = parser.parse_args()


#Feature = args.feature
Feature_list = args.feature.split(",")
Env_name = args.env_name
Email = args.email

for Feature in Feature_list:
    # Check if feature exists in mapping
    if not check_feature_exists(Feature):
        print("Feature ", Feature, " not found, skipping....")
        continue

    vms_name_mappings = get_feature_VMs(Feature)

    # Makes sure environment exist before checking content VMs
    Env_data = check_if_env_exists_return_data(Env_name, Email)

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
