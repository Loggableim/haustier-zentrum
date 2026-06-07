#!/usr/bin/env python3
import json

with open('C:/HermesPortable/home/auth.json', 'r') as f:
    auth = json.load(f)

or_creds = auth['credential_pool']['openrouter']
for cred in or_creds:
    token = cred.get('access_token', '')
    print(f"Key: {token[:30]}...{token[-10:]}")
    print(f"Source: {cred.get('source', '(none)')}")
