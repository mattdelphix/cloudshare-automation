from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--available_features", action="version", version="List all available Features: " + get_features())
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--feature", type=str, required=True, help="Feature to demo")
parser.add_argument("--email", type=str, required=True, help="Email of requestor")
args = parser.parse_args()

Env_name = args.env_name
Email = args.email
#Feature = args.feature
Feature_list = args.feature.split(",")

for Feature in Feature_list:
    # Check if feature exists in mapping
    if not check_feature_exists(Feature):
        print("Feature ", Feature, " not found, skipping....")
        continue

    blueprint_name_mappings = get_feature_blueprint(Feature)
    vms_name_mappings = get_feature_VMs(Feature)
    project_name_mappings = get_feature_project(Feature)

    #Makes sure environment exist before checking content VMs
    Env_data = check_if_env_exists_return_data(Env_name, Email)

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

    # Get machines info
    # blueprint_details = get_BlueprintInfo(project_ID, blueprint_ID)["createFromVersions"][0]["machines"]
    blueprint_default_details = get_allBlueprintInfo_default(project_ID)

    for i in range(len(blueprint_default_details)):
        if blueprint_default_details[i]["name"] == blueprint_name_mappings:
             # Loop for number of VMS
            for VM_Name in vms_name_mappings:
                if check_if_VM_exists_on_Env(Env_data, VM_Name):
                    for line in blueprint_default_details[i]["createFromVersions"][0]["machines"]:
                        if line["name"] == VM_Name:
                            VMsnapshot = {"id": line["id"], "name": line["name"]}
                            add_VM_from_snapshot(Env_data, VMsnapshot)
                            vm_execution_monitor(Env_data, VM_Name, "Running", "CREATE")
