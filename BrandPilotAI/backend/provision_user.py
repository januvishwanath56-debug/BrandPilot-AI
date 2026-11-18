"""Run locally; never commit output containing account configuration."""
import getpass
import json
from app.auth import password_hash

if __name__ == '__main__':
    username=input('Username: ').strip()
    role=input('Role (creator/reviewer/manager): ').strip()
    if not username or role not in ('creator','reviewer','manager'):
        raise SystemExit('Invalid account')
    password=getpass.getpass('Password (12+ characters): ')
    if len(password)<12:
        raise SystemExit('Use at least 12 characters')
    print(json.dumps({username:{'role':role,'password_hash':password_hash(password)}}))
