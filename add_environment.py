from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--desc", type=str, required=True, help="Description of the environment")
parser.add_argument("--project", type=str, required=True, help="Project Name to crete the environment on")
# parser.add_argument("--policy", type=str, required=True, help="Policy Name to create the environment with")
# parser.add_argument("--region", type=str, required=True, help="Region Name to create the environment on")
parser.add_argument("--email", type=str, required=True, help="Email of owner of new environment")
#parser.add_argument("--team", type=str, required=True, help="Team Email of owner of new environment")
parser.add_argument("--blueprint", type=str, required=True, help="Blueprint Name to create new environment from")
args = parser.parse_args()

# fixed variables for now
project_name = args.project
policy_name = "2 Weeks with Auto Suspend"
region_name = "US East (Miami)"
#team_name = args.team
blueprint_name = args.blueprint
env_name = args.env_name
description = args.desc
email = args.email

# Get Project ID from Project Name
projects = get_Projects()
project_ID = None
for line in projects:
    if line["name"] == project_name:
        project_ID = {"id": line["id"]}

if project_ID is None:
    print("Project " + project_name + " seems not to exist, exiting...")
    sys.exit(1)

# Get Policies ID from Policy Name
policies = get_Policies(project_ID)
policies_ID = None
for line in policies:
    if line["name"] == policy_name:
        policies_ID = {"id": line["id"]}

if policies_ID is None:
    print("Policy " + policy_name + " seems not to exist, exiting...")
    sys.exit(1)

# Get Region ID from Policy Name
region = get_Region()
region_ID = None
for line in region:
    if line["friendlyName"] == region_name:
        region_ID = {"id": line["id"]}

if region_ID is None:
    print("Region " + region_name + " seems not to exist, exiting...")
    sys.exit(1)

# Get Blueprint ID from name
blueprint = get_allBlueprintInfo(project_ID)
for line in blueprint:
    if line["name"] == blueprint_name:
        blueprint_ID = {"id": line["id"]}
if blueprint_ID is None:
    print("Blueprint Name: " + blueprint_name + " has not been found in Cloudshare")
    sys.exit(1)

# Get Snapshot ID from name
blueprint_details = get_BlueprintInfo(project_ID, blueprint_ID)["createFromVersions"]
# snapshot_name
# Check if VM exists in catalogs and if yes adds it and exits
snapshot_ID = None
for line in blueprint_details:
    if line["isLatest"]:
        snapshot_ID = {"id": line["id"]}

if snapshot_ID is None:
    print("Latest snapshot not found for this blueprint and project Cloudshare")
    sys.exit(1)

# Get team id for default group of 410000-Presales
#team_details = get_Team()
#team_ID = None
#for line in team_details:
#    if line["name"] == team_name:
#        team_ID = {"id": line["id"]}

#if team_ID is None:
#    print("Team Name: " + team_name + " has not been found in Cloudshare")
#    sys.exit(1)

# Ready to crete environment
# def add_env(name,description, project, policy, region, ownerEmail, team, blueprint, snapshot):
env_response = add_env(env_name, description, project_ID, policies_ID, region_ID, email, blueprint_ID, snapshot_ID)
new_env = {"id": env_response["environmentId"], "name": env_name}
env_execution_monitor(new_env, "Ready", "CREATE")
