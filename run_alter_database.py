#!/usr/bin/env python3
import datetime
import os.path
import subprocess
import sys

from env import env
from run_common import AWSCli
from run_common import check_template_availability
from run_common import print_message
from run_common import print_session

aws_cli = AWSCli()

print_session('alter database')

check_template_availability()

engine = env['rds']['ENGINE']
if engine not in ('aurora', 'aurora-mysql', 'aurora-postgresql'):
    print('not supported:', engine)
    raise Exception()

print_message('get database address')

if env['common']['PHASE'] != 'dv':
    db_host = aws_cli.get_rds_address()
else:
    while True:
        answer = input('Do you use a database of Vagrant VM? (yes/no): ')
        if answer.lower() == 'no':
            db_host = aws_cli.get_rds_address()
            break
        if answer.lower() == 'yes':
            db_host = 'dv-database.hbsmith.io'
            break

db_password = env['rds']['USER_PASSWORD']
db_user = env['rds']['USER_NAME']
template_name = env['template']['NAME']

print('/* YYYYMMDD list */')
list_dir = os.listdir('template/%s/rds/history' % template_name)
list_dir.sort()
print('\n'.join(list_dir))
yyyymmdd = str(input('\nplease input YYYYMMDD: '))
yyyymmdd_today = datetime.datetime.today().strftime('%Y%m%d')

if yyyymmdd < yyyymmdd_today:
    print('Not allow to alter with script older than today (%s).' % yyyymmdd_today)
    sys.exit(0)

print_message('alter data')

cmd_common = ['mysql']
cmd_common += ['-h' + db_host]
cmd_common += ['-u' + db_user]
cmd_common += ['-p' + db_password]

cmd = cmd_common + ['--comments']

filename = 'template/%s/rds/history/%s/mysql_schema_alter.sql' % (template_name, yyyymmdd)
if not os.path.exists(filename):
    print('file \'%s\' does not exists.' % filename)
    sys.exit(0)

with open(filename, 'r') as f:
    subprocess.Popen(cmd, stdin=f).communicate()
