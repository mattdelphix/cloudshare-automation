from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=False, help="Environment Name on CloudShare")
parser.add_argument("--feature", type=str, required=True, help="Feature to demo")
args = parser.parse_args()

if args.env_name is not None:
    Env_name = args.env_name
elif ENV_NAME is not None:
    Env_name = ENV_NAME

Feature = args.feature

blueprint_name_mappings = get_feature_blueprint(Feature)
vms_name_mappings = get_feature_VMs(Feature)
project_name_mappings = get_feature_project(Feature)

# Check if feature exists in mapping
if not check_feature_exists(Feature):
    print("Feature ", Feature, " not found, exiting....")
    sys.exit(1)

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
for VM_Name in vms_name_mappings:
    if check_if_VM_exists_on_Env(Env_data, VM_Name):
        for line in blueprint_details:
            if line["name"] == VM_Name:
                VMsnapshot = {"id": line["id"], "name": line["name"]}
                add_VM_from_snapshot(Env_data, VMsnapshot)
                vm_execution_monitor(Env_data, VM_Name, "Running", "CREATE")