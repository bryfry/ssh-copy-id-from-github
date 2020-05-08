
import pwd
import os
from typing import Union, List
from dataclasses import dataclass, field
from dataclasses_jsonschema import JsonSchemaMixin
from client import BaseClient

@dataclass
class Key(JsonSchemaMixin):
    id: int
    key: str

@dataclass
class GithubAuthorizedKeyFile(JsonSchemaMixin):
    github_users: Union[str,List[str]]
    path: str = field(init=False)
    keys: List[Key] = None
    user: str = None

    def __post_init__(self):
        if isinstance(self.github_users,str):
            self.github_users = [self.github_users]

        err, self.path = self.keyfile(user=self.user, write=True)


    async def collect_keys(self):
        for user in self.github_users:
          client = BaseClient(host="api.github.com", path=f"/users/{user}/keys") 
          err, data = await client.get_data()
          self.keys = [Key(**k) for k in data]
          

    def keyfile(self, user=None, write=False, path=None, manage_dir=True, follow=False):
        """
        Calculate name of authorized keys file, optionally creating the
        directories and file, properly setting permissions.
    
        :param str user: name of user in passwd file
        :param bool write: if True, write changes to authorized_keys file (creating directories if needed)
        :param str path: if not None, use provided path rather than default of '~user/.ssh/authorized_keys'
        :param bool manage_dir: if True, create and set ownership of the parent dir of the authorized_keys file
        :param bool follow: if True symlinks will be followed and not replaced
        :return: full path string to authorized_keys for user
        """
    
        try:
            if user is None:
                user_entry = pwd.getpwuid(os.getuid())
            else: 
                user_entry = pwd.getpwnam(user)
        except KeyError as e:
            return (f"Failed to lookup user {user}: {e}", None)
    
        if path is None:
            homedir = user_entry.pw_dir
            sshdir = os.path.join(homedir, ".ssh")
            keysfile = os.path.join(sshdir, "authorized_keys")
        else:
            sshdir = os.path.dirname(path)
            keysfile = path
    
        if follow:
            keysfile = os.path.realpath(keysfile)
    
        if not write:
            return (None, keysfile)
    
        uid = user_entry.pw_uid
        gid = user_entry.pw_gid
    
        if manage_dir:
            if not os.path.exists(sshdir):
                os.mkdir(sshdir, int('0700', 8))
            os.chown(sshdir, uid, gid)
            os.chmod(sshdir, int('0700', 8))
    
        if not os.path.exists(keysfile):
            basedir = os.path.dirname(keysfile)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            try:
                f = open(keysfile, "w")  # touches file so we can set ownership and perms
            finally:
                f.close()
    
        try:
            os.chown(keysfile, uid, gid)
            os.chmod(keysfile, int('0600', 8))
        except OSError:
            pass
    
        return (None, keysfile)

    def writefile(filename, content):
    
        fd, tmp_path = tempfile.mkstemp('', 'tmp', os.path.dirname(filename))
        f = open(tmp_path, "w")
    
        try:
            f.write(content)
        except IOError as e:
            return (f"Failed to write to file {tmp_path}: {e}", None)
        f.close()
        #module.atomic_move(tmp_path, filename)
