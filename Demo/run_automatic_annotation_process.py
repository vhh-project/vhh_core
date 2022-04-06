import argparse

from MainController import MainController

parser = argparse.ArgumentParser()

# Make the module to run selectible
parser.add_argument('--run_pipeline_on_all_videos', action='store_true')
parser.add_argument('--run_only_packages',  action='store', dest='packages',
                    type=str, nargs='*', default=["SBD", "STC", "OD", "CMC"],
                    help="Runs the only the selected packages. Examples: --run_packages_on_all_videos SBD STC OD CMC")
args = parser.parse_args()
main_instance = MainController()

main_instance.run(run_on_all_videos=args.run_pipeline_on_all_videos,
                  packages_to_run=args.packages)
