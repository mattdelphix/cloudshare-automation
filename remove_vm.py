from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=True, help="Environment Name on CloudShare")
parser.add_argument("--vm_name", type=str, required=True, help="VM to remove")
parser.add_argument("--email", type=str, required=True, help="Email of requestor")
args = parser.parse_args()

Env_name = args.env_name
VM_Name = args.vm_name
Email = args.email

# Makes sure environment exist before checking content VMs
Env_data = check_if_env_exists_return_data(Env_name)

# Makes sure the owner of the environment is the caller of the script
if not check_if_email_exists(Env_data, Email):
    sys.exit(1)

# Check if VM exists on the environment
vm_exists = False
res = get_env_status(Env_data)["vms"]
for x in res:
    if x["name"] == VM_Name:
        VM = {"id": x["id"], "name": x["name"]}
        delete_VM(VM)
        vm_execution_monitor(Env_data, VM_Name, "Deleted", "DELETE")
        vm_exists = True

if not vm_exists:
    print("VM with name " + VM_Name + " does not seem to exist on this environment " + Env_name)
