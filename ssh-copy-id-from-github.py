import argparse
import asyncio
from authorized_key import GithubAuthorizedKeyFile


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "users", metavar="username", type=str, nargs='+',
         help="Public key source Github usernames", 
    )
    parser.add_argument(
         "-a", "--annotate", dest='annotate', action='store_true',
         help="store public key source details in key annotation"
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
         "-O", "--to-stdout", dest='stdout', action='store_true',
         help="write results to standard output"
    )
    output_group.add_argument(
         "-f", "--file", type=str, default=None,
         help="store output in FILE"
    )
    parser.add_argument(
         "-u", "--user", type=str, default=None,
         help="store output for USER"
    )
    parser.set_defaults(stdout=False, annotate=False)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    loop = asyncio.get_event_loop()
    ak = GithubAuthorizedKeyFile(
        github_users=args.users,
        annotate=args.annotate,
        user=args.user,
        filename=args.file
    )
    loop.run_until_complete(ak.collect_keys())
    
    if args.stdout:
        print(ak.serialize())
    else:
        ak.writefile()
