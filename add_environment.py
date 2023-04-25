from cloudshare_functions import *

parser = argparse.ArgumentParser(description='CloudShare API Operations')
parser.add_argument('--version', action='version', version='%(prog)s Version ' + version)
parser.add_argument("--env_name", type=str, required=False, help="Environment Name on CloudShare")
parser.add_argument("--feature", type=str, required=True, help="Feature to demo")
args = parser.parse_args()

