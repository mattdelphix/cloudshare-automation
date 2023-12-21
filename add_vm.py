from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--vm_name", type=str, required=True, help="VM to add to env")
parser.add_argument("--project_name", type=str, required=True, help="Project Name where the VM exists")
parser.add_argument("--blueprint_name", type=str, required=True, help="Blueprint where the VM exists")
parser.add_argument("--email", type=str, required=True, help="Email of requestor")
args = parser.parse_args()

VM_Name = args.vm_name
Project_Name = args.project_name
Blueprint_Name = args.blueprint_name
Env_name = args.env_name
Email = args.email

#Makes sure environment exist before checking content VMs
Env_data = check_if_env_exists_return_data(Env_name, Email)

# Check if VM exists on the environment
if not check_if_VM_exists_on_Env(Env_data, VM_Name):
    sys.exit(1)

#Get Project ID from Project Name info to later get VM ID
project_ID = None
projects = get_Projects()
for line in projects:
    if line["name"] == Project_Name:
        project_ID = {"id": line["id"]}
if project_ID is None:
    print("Project Name: " + Project_Name + " has not been found in Cloudshare")
    sys.exit(1)

#Get Blueprint info to later get VM ID
blueprint_ID = None
project_info = get_allBlueprintInfo(project_ID)
for line in project_info:
    if line["name"] == Blueprint_Name:
        blueprint_ID = {"id": line["id"]}
if blueprint_ID is None:
    print("Blueprint Name: " + Blueprint_Name + " has not been found in Cloudshare")
    sys.exit(1)

#Get default machines info
blueprint_details = find_default_BlueprintInfo(get_BlueprintInfo(project_ID, blueprint_ID)["createFromVersions"])

#Check if VM exists in catalogs and if yes adds it and exits
flag_found = False
for line in blueprint_details:
    if line["name"] == VM_Name:
        flag_found = True
        VMsnapshot = {"id": line["id"], "name": line["name"]}
        add_VM_from_snapshot(Env_data, VMsnapshot)
        vm_execution_monitor(Env_data, VM_Name, "Running", "CREATE")

if not flag_found:
    print("VM with name " + VM_Name + " was not found in the blueprint " + Blueprint_Name)
