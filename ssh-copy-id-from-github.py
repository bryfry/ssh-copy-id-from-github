import argparse
import asyncio
from authorized_key import GithubAuthorizedKeyFile


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "users", metavar="user", type=str, nargs='+',
         help="Github Users to add public keys from (source)", 
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    loop = asyncio.get_event_loop()
    ak = GithubAuthorizedKeyFile(github_users=args.users)
    print (ak)    
    loop.run_until_complete(ak.collect_keys())
    print (ak)    
    # TODO write to file

