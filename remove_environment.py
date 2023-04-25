from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
args = parser.parse_args()

#Makes sure environment exist before checking content VMs
#If it does not exist the it exits on the fist function
Env_data = check_if_env_exists_return_data(args.env_name)
print("Attempting to remove environment " + Env_data["name"])
remove_env(Env_data)

