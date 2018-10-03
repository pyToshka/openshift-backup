# -*- coding: utf-8 -*-

import datetime
import errno
import os

import configparser
import kubernetes.client
import urllib3
from kubernetes import client
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
from openshift import watch

now = datetime.datetime.now()
urllib3.disable_warnings()
config = configparser.ConfigParser()
config.read('config.ini')
token = config['default']['api_key']
openhsift_hostname = config['default']['openshift_host_name']
openshift_port = config['default']['openshift_port']
directory = config['backup']['directory']
configuration = kubernetes.client.Configuration()
configuration.host = openhsift_hostname + ":" + openshift_port
configuration.verify_ssl = False
configuration.debug = False
configuration.assert_hostname = False
configuration.api_key = {"authorization": "Bearer " + token}
client.Configuration.set_default(configuration)
api = core_v1_api.CoreV1Api()
os.chdir(os.path.dirname(__file__))
project_directory=(os.getcwd())
date=now.strftime("%Y-%m-%d-%H:%M")
try:
    os.makedirs(project_directory+"/"+directory)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

def main():
    v1 = client.CoreV1Api()
    count = 10000
    w = watch.Watch()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for event in ret.items:

        dict=event.metadata.labels.get('backup')
        if dict is None:  # Check if key is there, but None
            dict = []
        else:
            dict
            print("Pod name is: %s and tag is %s" % (event.metadata.name, dict))
        if dict=="postgresql":
            print "backup postgresql"
            backup_postgresql(event.metadata.name,event.metadata.namespace,dict)
        if dict=="mysql":
            print "backup mysql"
            backup_mysql(event.metadata.name,event.metadata.namespace,dict)
        count -= 1
        if not count:
            w.stop()


def backup_postgresql(pod,namespace,tag):
    dump_directory=project_directory + "/" + directory+"/"+tag
    try:
        os.makedirs(dump_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    exec_command = [
        '/bin/bash'
    ]
    resp = stream(api.connect_get_namespaced_pod_exec, pod,namespace,
                  command=exec_command,
                  stderr=True, stdin=True,
                  stdout=True, tty=False,
                  _preload_content=False)
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
            db_name = resp.read_stdout()
            print(db_name)
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
        if exec_command:
            c = exec_command.pop(0)
            db_name = resp.read_stdout()
            backup_comand = [
                '/bin/bash', '-c', 'pg_dump -Fp $POSTGRESQL_DATABASE ', '>',
                '$POSTGRESQL_DATABASE.pg_dump_custom'
            ]
            
            with open(dump_directory+"/"+pod+"-"+tag+"-"+date+".dmp", 'w') as file_buffer:
    
                resp = stream(api.connect_get_namespaced_pod_exec,pod, namespace,
                            command=backup_comand,
                            stderr=True, stdin=True,
                            stdout=True, tty=True,
                            _preload_content=False)
                while resp.is_open():
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        out = resp.read_stdout()
                        file_buffer.write(out)
                    if resp.peek_stderr():
                        print("STDERR: %s" % resp.read_stderr())
                resp.close()
                file_buffer.close()
            
        else:
            break
        
def backup_mysql(pod,namespace,tag):
    dump_directory = project_directory + "/" + directory + "/" + tag
    try:
        os.makedirs(dump_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    exec_command = [
        '/bin/bash'
    ]
    resp = stream(api.connect_get_namespaced_pod_exec, pod, namespace,
                  command=exec_command,
                  stderr=True, stdin=True,
                  stdout=True, tty=False,
                  _preload_content=False)
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
            db_name = resp.read_stdout()
            print(db_name)
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
        if exec_command:
            c = exec_command.pop(0)
            db_name = resp.read_stdout()
            backup_comand = [
                '/bin/bash', '-c', 'mysqldump -h 127.0.0.1 -u $MYSQL_USER --password=$MYSQL_PASSWORD $MYSQL_DATABASE', '>',
                '$MYSQL_DATABASE.mysql_dump_custom'
            ]
            
            with open(dump_directory+"/"+pod+"-"+tag+"-"+date+".dmp", 'w') as file_buffer:
                
                resp = stream(api.connect_get_namespaced_pod_exec, pod, namespace,
                              command=backup_comand,
                              stderr=True, stdin=True,
                              stdout=True, tty=True,
                              _preload_content=False)
                while resp.is_open():
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        out = resp.read_stdout()
                        file_buffer.write(out)
                    if resp.peek_stderr():
                        print("STDERR: %s" % resp.read_stderr())
                resp.close()
                file_buffer.close()
        
        else:
            break
    


if __name__ == '__main__':
    main()
  