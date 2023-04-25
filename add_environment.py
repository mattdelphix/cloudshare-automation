from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--project", type=str, required=True, help="Project Name to crete the environment on")
parser.add_argument("--policy", type=str, required=True, help="Policy Name to crete the environment with")
parser.add_argument("--region", type=str, required=True, help="Region Name to crete the environment on")
parser.add_argument("--region", type=str, required=True, help="Region Name to crete the environment on")
parser.add_argument("--email", type=str, required=True, help="Email of owner of new environment")
parser.add_argument("--blueprint", type=str, required=True, help="Blueprint Name to create new environment from")
parser.add_argument("--Snapshot", type=str, required=True, help="Snapshot Name to create new environment from")
args = parser.parse_args()

#we need to get the ID for project, policy, region, ownerEmail, team, blueprint, snapshot