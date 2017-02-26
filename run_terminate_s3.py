#!/usr/bin/env python3
from __future__ import print_function

import json
import subprocess

from env import env
from run_common import AWSCli
from run_common import print_message
from run_common import print_session

args = []

if __name__ == "__main__":
    from run_common import parse_args

    args = parse_args()

aws_cli = AWSCli()


def run_terminate_s3_webapp(name, settings):
    print_message('terminate ' + name)
    deploy_bucket_name = settings['BUCKET_NAME']

    ################################################################################
    print_message('cleanup deploy bucket')

    cmd = ['s3', 'rm', 's3://%s/' % deploy_bucket_name, '--recursive']
    upload_result = aws_cli.run(cmd)
    for ll in upload_result.split('\n'):
        print(ll)

    cmd = ['s3api', 'delete-bucket-tagging', '--bucket', deploy_bucket_name]
    aws_cli.run(cmd)

    ################################################################################
    print_message('purge cache from cloudflare')

    cf_api_key = env['common']['CLOUDFLARE_API_KEY']
    cf_auth_email = env['common']['CLOUDFLARE_AUTH_EMAIL']
    cf_zone_id = env['common']['CLOUDFLARE_ZONE_ID']
    cf_endpoint = 'https://api.cloudflare.com/client/v4/zones/%s/purge_cache' % cf_zone_id

    data = dict()
    data['files'] = list(settings['PURGE_FILES'])

    cmd = ['curl', '-X', 'DELETE', cf_endpoint,
           '-H', 'X-Auth-Email: %s' % cf_auth_email,
           '-H', 'X-Auth-Key: %s' % cf_api_key,
           '-H', 'Content-Type: application/json',
           '--data', json.dumps(data)]

    subprocess.Popen(cmd).communicate()


################################################################################
#
# start
#
################################################################################
print_session('terminate eb')

s3 = env['s3']
if len(args) == 2:
    target_s3_name = args[1]
    for s3_env in s3:
        if s3_env['NAME'] == target_s3_name:
            if s3_env['TYPE'] == 'webapp':
                run_terminate_s3_webapp(s3_env['NAME'], s3_env)
                break
    print('"%s" is not exists in config.json' % target_s3_name)
else:
    for s3_env in s3:
        if s3_env['TYPE'] == 'webapp':
            run_terminate_s3_webapp(s3_env['NAME'], s3_env)
