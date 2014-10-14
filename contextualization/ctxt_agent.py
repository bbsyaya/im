#! /usr/bin/env python
# IM - Infrastructure Manager
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from optparse import OptionParser
import time
import logging
import logging.config
import sys, subprocess, os
import getpass
import json
import threading

from SSH import SSH


SSH_WAIT_TIMEOUT = 600
# This value enables to retry the playbooks to avoid some SSH connectivity problems
# The minimum value is 1
PLAYBOOK_RETRIES = 3


def wait_ssh_access(vm):
	"""
	 Test the SSH access to the VM
	"""
	delay = 10
	wait = 0
	while wait < SSH_WAIT_TIMEOUT:
		logger.debug("Testing SSH access to VM: " + vm['ip'])
		wait += delay
		ssh_client = SSH(vm['ip'], vm['user'], vm['passwd'], vm['private_key'], vm['ssh_port'])
		if ssh_client.test_connectivity():
			return True
		else:
			time.sleep(delay)
	
	return False

def run_command(command, timeout = None, poll_delay = 5):
	"""
	 Function to run a command
	"""
	try:
		p=subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		
		if timeout is not None:
			wait = 0
			while p.poll() is None and wait < timeout:
				time.sleep(poll_delay)
				wait += poll_delay

			if p.poll() is None:
				p.kill()
				return "TIMEOUT"

		(out, err) = p.communicate()
		
		if p.returncode!=0:
			return "ERROR: " + err + out
		else:
			return out
	except Exception, ex:
		return "ERROR: Exception msg: " + str(ex)


def wait_processes(procs_list, poll_delay = 5):
	"""
	 Wait for a list of processes (Popen objects) to finish
	"""
	allok = True
	if len(procs_list) > 0:
		logger.debug('Processes launched, wait.')
		for p in procs_list:
			(out, err) = p.communicate()
			
			if p.returncode==0:
				logger.debug(out + "\n" + err)
			else:
				allok = False
				logger.debug(out + "\n" + err)

	return allok

def LaunchAnsiblePlaybook(playbook_file, vm, threads, pk_file = None):
	command = "/usr/bin/python_ansible " + conf_dir + "/ansible-playbook"
	command += " -f " + str(2*threads)
	
	if pk_file:
		command += " --private-key " + pk_file
	else:
		command += " -u " + vm['user']
		if vm['private_key'] and not vm['passwd']:
			gen_pk_file = "/tmp/pk_" + vm['ip'] + ".pem"
			# If the file exists do not create it again
			if not os.path.isfile(gen_pk_file):
				pk_out = open(gen_pk_file, 'w')
				pk_out.write(vm['private_key'])
				pk_out.close()
				os.chmod(gen_pk_file,0400)
			
			command += " --private-key " + gen_pk_file
		else:
			command += " -p '" + vm['passwd'] + "'"
		
	command += " " + playbook_file
	
	logger.debug('Call Ansible: ' + command)
	
	return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

def launch_playbook_processes(group_list, conf_dir, prefix, playbook):
	procs_list = []

	for group in group_list:
		for vm in group['vms']:
			out = open(conf_dir + "/" + prefix + vm['ip'] + ".yml", 'w')
			out.write(playbook)
			out.write("  hosts: " + vm['ip'] + "\n")
			out.close()
			
			playbook_file = conf_dir + "/" + prefix + vm['ip'] + ".yml"
			ansible_process = LaunchAnsiblePlaybook(playbook_file, vm, 1)
			procs_list.append(ansible_process)

	allok = wait_processes(procs_list)
	
	for group in group_list:
		# Delete the YAML created files
		for vm in group['vms']:
			os.remove(conf_dir + "/" + prefix + vm['ip'] + ".yml")
	
	return allok


def changeVMCredentials(vm, res):
	# Check if we must change user credentials in the VM
	# Do not change the IP of the master. It must be changed only by the ConfManager
	if not vm['master']:
		if 'new_passwd' in vm and vm['new_passwd']:
			logger.info("Changing password to VM: " + vm['ip'])
			ssh_client = SSH(vm['ip'], vm['user'], vm['passwd'], vm['private_key'], vm['ssh_port'])
			(out, err, code) = ssh_client.execute('sudo bash -c \'echo "' + vm['user'] + ':' + vm['new_passwd'] + '" | chpasswd && echo "OK"\' 2> /dev/null')
			
			if code == 0:
				res[vm['ip']] = True
				vm['passwd'] = vm['new_passwd']
			else:
				res[vm['ip']] = False
				logger.error("Error changing password to VM:: " + vm['ip'] + ". " + out + err)

		if 'new_public_key' in vm and vm['new_public_key'] and 'new_private_key' in vm and vm['new_private_key']:
			logger.info("Changing public key to VM: " + vm['ip'])
			ssh_client = SSH(vm['ip'], vm['user'], vm['passwd'], vm['private_key'], vm['ssh_port'])
			(out, err, code) = ssh_client.execute('echo ' + vm['new_public_key'] + ' >> .ssh/authorized_keys')
			if code != 0:
				res[vm['ip']] = False
				logger.error("Error changing public key to VM:: " + vm['ip'] + ". " + out + err)
			else:
				res[vm['ip']] = True
				vm['private_key'] = vm['new_private_key']


def changeCredentials(group_list):
	# Check if we must change user credentials
	res = {}
	thread_list = []
	for group in group_list:
		for vm in group['vms']:
			t = threading.Thread(target = changeVMCredentials, args = (vm, res))
			t.start()
			thread_list.append(t)
	
	for t in thread_list:
		t.join()

	return res

def generateBasicPlaybook(conf_dir, pk_file):
	""" Generate the playbook with the basic tasks to configure the nodes """
	
	with open(conf_dir + '/basic.yml') as f: basic_play = f.read()
	basic_play += "\n  vars:\n" 
	basic_play += "    - pk_file: " + pk_file + ".pub\n\n"

	return basic_play

def contextualizeGroups(group_list, contextualize_list, conf_dir):
	res_data = {}
	pk_file = "/tmp/ansible_key"
	logger.info('Generate and copy the ssh key')
	
	# If the file exists, do not create it again
	if not os.path.isfile(pk_file):
		out = run_command('ssh-keygen -t rsa -C ' + getpass.getuser() + ' -q -N "" -f ' + pk_file)
		logger.debug(out)

	# Check that we can SSH access the nodes
	for group in group_list:
		for vm in group['vms']:
			logger.info("Waiting SSH access to VM: " + vm['ip'])
			if not wait_ssh_access(vm):
				logger.error("Error Waiting SSH access to VM: " + vm['ip'])
				res_data['SSH_WAIT'] = False
				res_data['OK'] = False
				return res_data
			else:
				res_data['SSH_WAIT'] = True
				logger.info("SSH access to VM: " + vm['ip']+ " Open!")
	
	# Generate the basic playbook
	basic_play = generateBasicPlaybook(conf_dir, pk_file)

	# And launch the threads to configure the basic tasks
	cont = 0
	allok = False
	while not allok and cont < PLAYBOOK_RETRIES:
		cont += 1
		allok = launch_playbook_processes(group_list, conf_dir, "basic_",basic_play)
		if allok:
			res_data['BASIC'] = True
			logger.info("Basic playbook executed successfully.")
		else:
			logger.error("Error executing basic playbook.")
			res_data['BASIC'] = False
			res_data['OK'] = False
			return res_data
	
	# Now we can access all the VMs with SSH without password
		
	res_data['OK'] = True

	group_forks = {}
	# First execute the "main" playbook
	cont = 0
	mainok = False
	while not mainok and cont < PLAYBOOK_RETRIES:
		cont += 1
		procs_list = []
		for group in group_list:
			# get the number of VMs to use it later
			group_forks[group['name']] = len(group['vms'])
			logger.info('Launch the main playbook to the group: ' + group['name'] + " with " + str(len(group['vms'])) + " forks")
			playbook = conf_dir + "/main_" + group['name'] + "_all.yml"
	
			ansible_process = LaunchAnsiblePlaybook(playbook, None, len(group['vms']), pk_file)
			time.sleep(2)
			procs_list.append(ansible_process)
			
		mainok = wait_processes(procs_list)
	
		if not mainok:
			res_data['MAIN'] = False
			res_data['OK'] = False
			logger.error("Error executing the main playbook.")
			return res_data
		else:
			res_data['MAIN'] = True

	# Now execute the other playbooks grouped using the  "contxt_num"
	for contxt_num in sorted(contextualize_list.keys()):
		cont = 0
		groupok = False
		res_data['CTXT'] = {}
		while not groupok and cont < PLAYBOOK_RETRIES:
			logger.info('Executing the playbooks with contextualization level: ' + str(contxt_num))
			cont += 1
			procs_list = []
			for contextualize_elem in contextualize_list[contxt_num]:
				system = contextualize_elem['system']
				configure = contextualize_elem['configure']
				logger.info('Launch the thread for the playbook ' + configure + ' for the group: ' + system + " with " + str(group_forks[system]) + " forks")
				playbook = conf_dir + "/" + configure + "_" + system + "_all.yml"
				
				ansible_process = LaunchAnsiblePlaybook(playbook, None, group_forks[system], pk_file)
				procs_list.append(ansible_process)
			
			groupok = wait_processes(procs_list)
			
			if not groupok:
				logger.error('Error executing the playbooks with contextualization level: ' + str(contxt_num))
				res_data['CTXT'][contxt_num] = False
				res_data['OK'] = False
			else:
				res_data['CTXT'][contxt_num] = True

	# Finally check if we must chage user credentials
	res_data['CHANGE_CREDS'] = changeCredentials(group_list)

	logger.info('Process finished')
	return res_data

if __name__ == "__main__":
	parser = OptionParser(usage="%prog [input_file]", version="%prog 1.0")
	(options, args) = parser.parse_args()
	
	if len(args) != 1:
		parser.error("Error: Incorrect parameters")
	
	conf_path = os.path.dirname(sys.argv[0])
	if conf_path.strip() == '':
		conf_path = '.'
	
	# Root logger: is used by paramiko
	logging.basicConfig(filename=conf_path+"/ctxt_agent.log",
			    level=logging.WARNING,
			    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
			    datefmt='%m-%d-%Y %H:%M:%S')
	# ctxt_agent logger
	logger = logging.getLogger('ctxt_agent')
	logger.setLevel(logging.DEBUG)
	
	conf_dir="/tmp/conf"
	MAX_SSH_WAIT = 60
	
	# load json conf data
	conf_data = json.load(open(args[0]))

	success = False
	if 'groups' in conf_data and 'contextualizes' in conf_data:
		res_data = contextualizeGroups(conf_data['groups'], conf_data['contextualizes'], conf_dir)
	
	ctxt_out = open(conf_path+"/ctxt_agent.out", 'w')
	json.dump(res_data, ctxt_out, indent=2)
	ctxt_out.close()

	if res_data['OK']:
		sys.exit(0)
	else:
		sys.exit(1)
