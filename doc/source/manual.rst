
IM Service Installation
=======================

Prerequisites
-------------

IM needs at least Python 2.6 to run, as well as the next libraries:

* `The RADL parser <https://github.com/grycap/radl>`_.
  (Since IM version 1.5.3, it requires RADL version 1.1.0 or later).
* `paramiko <http://www.lag.net/paramiko/>`_, ssh2 protocol library for python
  (version 1.14 or later).
* `PyYAML <http://pyyaml.org/>`_, a YAML parser.
* `suds <https://fedorahosted.org/suds/>`_, a full-featured SOAP library.
* `Netaddr <http://pythonhosted.org/netaddr//>`_, A Python library for representing 
  and manipulating network addresses.
* `Requests <http://docs.python-requests.org>`_, A Python library for access REST APIs.
    
Also, IM uses `Ansible <http://www.ansible.com>`_ (1.4.2 or later) to configure the
infrastructure nodes. The current recommended version is 1.9.4 untill the 2.X versions become stable.
 
These components are usually available from the distribution repositories.
   
Finally, check the next values in the Ansible configuration file
:file:`ansible.cfg`, (usually found in :file:`/etc/ansible`)::

   [defaults]
   transport  = smart
   host_key_checking = False
   
   # For old versions 1.X
   sudo_user = root
   sudo_exe = sudo
   
   # For new versions 2.X
   become_user      = root
   become_method    = sudo
   
   [paramiko_connection]
   
   record_host_keys=False
   
   [ssh_connection]
   
   # Only in systems with OpenSSH support to ControlPersist
   ssh_args = -o ControlMaster=auto -o ControlPersist=900s
   # In systems with older versions of OpenSSH (RHEL 6, CentOS 6, SLES 10 or SLES 11) 
   #ssh_args =
   pipelining = True

Optional Packages
-----------------

* `The Bottle framework<http://bottlepy.org/>`_ is used for the REST API. 
   It is typically available as the 'python-bottle' package.
* `The CherryPy Web framework <http://www.cherrypy.org/>`_, is needed for the REST API. 
   It is typically available as the 'python-cherrypy' or 'python-cherrypy3' package.
   In newer versions (9.0 and later) the functionality has been moved `the cheroot
   library<https://github.com/cherrypy/cheroot>`_ it can be installed using pip.
* `apache-libcloud <http://libcloud.apache.org/>`_ 0.17 or later is used in the
  LibCloud, OpenStack and GCE connectors.
* `boto <http://boto.readthedocs.org>`_ 2.29.0 or later is used as interface to
  Amazon EC2. It is available as package named ``python-boto`` in Debian based
  distributions. It can also be downloaded from `boto GitHub repository <https://github.com/boto/boto>`_.
  Download the file and copy the boto subdirectory into the IM install path.
* pyOpenSSL are needed if needed to secure the REST API
  with SSL certificates (see :confval:`REST_SSL`).
  pyOpenSSL can be installed using pip.
* `The Python interface to MySQL <https://www.mysql.com/>`_, is needed to access MySQL server as IM data 
  backend. It is typically available as the package 'python-mysqldb' or 'MySQL-python' package. In case of
  using Python 3 use the PyMySQL package, available as the package 'python3-pymysql' on debian systems or PyMySQL
  package in pip.  
* `The Azure Python SDK <https://docs.microsoft.com/es-es/azure/python-how-to-install/>`_, is needed by the Azure
  connector. It is available as the package 'azure' at the pip repository.  

Installation
------------

From Pip (Recommended option)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**WARNING: In some linux old distributions (REL 6 or equivalents) you must unistall
the package python-crypto and python-paramiko before installing the IM with pip.**::

	$ rpm -e python-crypto python-paramiko --nodeps

First you need to install pip tool and some packages needed to compile some of the IM requirements.
To install them in Debian and Ubuntu based distributions, do::

    $ apt update
    $ apt install gcc python-dev libffi-dev libssl-dev python-pip sshpass python-pysqlite2 python-requests

In Red Hat based distributions (RHEL, CentOS, Amazon Linux, Oracle Linux,
Fedora, etc.), do::

	$ yum install epel-release
	$ yum install which gcc python-devel libffi-devel openssl-devel python-pip sshpass python-sqlite3dbm

For some problems with the dependencies of the apache-libcloud package in some systems (as ubuntu 14.04 or CentOS 6)
this package has to be installed manually::

	$ pip install backports-ssl_match_hostname

Then you only have to call the install command of the pip tool with the IM package::

	$ pip install IM

Pip will also install the, non installed, pre-requisites needed. So Ansible 1.4.2 or later will 
be installed in the system. Some of the optional packages are also installed please check if some
of IM features that you need requires to install some of the packages of section "Optional Packages". 

You must also remember to modify the ansible.cfg file setting as specified in the 
"Prerequisites" section.

From RPM packages (RH7)
^^^^^^^^^^^^^^^^^^^^^^^
Download the RPM package from `GitHub <https://github.com/grycap/im/releases/latest>`_. 
Also remember to download the RPM of the RADL package also from `GitHub <https://github.com/grycap/radl/releases/latest>`_. 
You must have the epel repository enabled:: 

   $ yum install epel-release
   
Then install the downloaded RPMs:: 

   $ yum localinstall IM-*.rpm RADL-*.rpm
   
Azure python SDK is not available in CentOS. So if you need the Azure plugin you have to manually install them using pip::

	$ pip install msrest msrestazure azure-common azure-mgmt-storage azure-mgmt-compute azure-mgmt-network azure-mgmt-resource

From Deb package (Tested with Ubuntu 14.04 and 16.04)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Download the Deb package from `GitHub <https://github.com/grycap/im/releases/latest>`_
Also remember to download the Deb of the RADL package also from `GitHub <https://github.com/grycap/radl/releases/latest>`_.

In Ubuntu 14.04 there are some requisites not available for the "trusty" version or are too old, so you have to manually install them manually.
You can download it from their corresponding PPAs. But here you have some links:
 
 * python-backports.ssl-match-hostname: `download <http://archive.ubuntu.com/ubuntu/pool/universe/b/backports.ssl-match-hostname/python-backports.ssl-match-hostname_3.4.0.2-1_all.deb>`_
 * python-scp: `download <http://archive.ubuntu.com/ubuntu/pool/universe/p/python-scp/python-scp_0.10.2-1_all.deb>`_
 * python-libcloud: `download <http://archive.ubuntu.com/ubuntu/pool/universe/libc/libcloud/python-libcloud_0.20.0-1_all.deb>`_

Also Azure python SDK is not available in Ubuntu 16.04. So if you need the Azure plugin you have to manually install them.
You can download it from their corresponding PPAs. But here you have some links:

 * python-msrestazure: `download <https://launchpad.net/ubuntu/+archive/primary/+files/python-msrestazure_0.4.3-1_all.deb>`_
 * python-msrest: `download <https://launchpad.net/ubuntu/+archive/primary/+files/python-msrest_0.4.4-1_all.deb>`_
 * python-azure: `download <https://launchpad.net/ubuntu/+archive/primary/+files/python-azure_2.0.0~rc6+dfsg-2_all.deb>`_

It is also recommended to configure the Ansible PPA to install the newest versions of Ansible (see `Ansible installation <http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-apt-ubuntu>`_)::

	$ sudo apt-get install software-properties-common
	$ sudo apt-add-repository ppa:ansible/ansible
	$ sudo apt-get update

Put all the .deb files in the same directory and do::

	$ sudo dpkg -i *.deb
	$ sudo apt install -f -y

From Source
^^^^^^^^^^^

Once the dependences are installed, just download the tarball of *IM Service*
from `Download <https://github.com/grycap/im>`_, extract the 
content and move the extracted directory to the installation path (for instance
:file:`/usr/local` or :file:`/opt`)::

   $ tar xvzf IM-0.1.tar.gz
   $ sudo chown -R root:root IM-0.1.tar.gz
   $ sudo mv IM-0.1 /usr/local

Finally you must copy (or link) $IM_PATH/scripts/im file to /etc/init.d directory::

   $ sudo ln -s /usr/local/IM-0.1/scripts/im /etc/init.d

Configuration
-------------

If you want the IM Service to be started at boot time, do

1. Update the value of the variable ``IMDAEMON`` in :file:`/etc/init.d/im` file
   to the path where the IM im_service.py file is installed (e.g. /usr/local/im/im_service.py),
   or set the name of the script file (im_service.py) if the file is in the PATH
   (pip puts the im_service.py file in the PATH as default)::

   $ sudo sed -i 's/`IMDAEMON=.*/`IMDAEMON=/usr/local/IM-0.1/im_service.py'/etc/init.d/im

2. Register the service.

To do the last step on a Debian based distributions, execute::

   $ sudo sysv-rc-conf im on

if the package 'sysv-rc-conf' is not available in your distribution, execute::

   $ sudo update-rc.d im start 99 2 3 4 5 . stop 05 0 1 6 .

For Red Hat based distributions::

   $ sudo chkconfig im on

Alternatively, it can be done manually::

   $ ln -s /etc/init.d/im /etc/rc2.d/S99im
   $ ln -s /etc/init.d/im /etc/rc3.d/S99im
   $ ln -s /etc/init.d/im /etc/rc5.d/S99im
   $ ln -s /etc/init.d/im /etc/rc1.d/K05im
   $ ln -s /etc/init.d/im /etc/rc6.d/K05im

IM reads the configuration from :file:`$IM_PATH/etc/im.cfg`, and if it is not
available, does from ``/etc/im/im.cfg``. There is a template of :file:`im.cfg`
at the directory :file:`etc` on the tarball. The IM reads the values of the ``im``
section. The options are explained next.

.. _options-basic:

Basic Options
^^^^^^^^^^^^^

.. confval:: DATA_FILE

   Full path to the data file.
   (**Removed in version IM version 1.5.0. Use only DATA_DB.**) 
   The default value is :file:`/etc/im/inf.dat`.

.. confval:: DATA_DB

   The URL to access the database to store the IM data.
   It can be a MySQL DB: 'mysql://username:password@server/db_name' or 
   a SQLite one: 'sqlite:///etc/im/inf.dat'.
   The default value is ``sqlite:///etc/im/inf.dat``.
   
.. confval:: USER_DB

   Full path to the IM user DB json file.
   To restrict the users that can access the IM service.
   Comment it or set a blank value to disable user check.
   The default value is empty.
   JSON format of the file::
   
   	{
   		"users": [
   			{
   				"username": "user1",
   				"password": "pass1"
   			},
   			{
   				"username": "user2",
   				"password": "pass2"
   			}
   		]
   	}
   
.. confval:: MAX_SIMULTANEOUS_LAUNCHES

   Maximum number of simultaneous VM launch operations.
   In some versions of python (prior to 2.7.5 or 3.3.2) it can raise an error 
   ('Thread' object has no attribute '_children'). See https://bugs.python.org/issue10015.
   In this case set this value to 1
   
   The default value is 1.
 
.. confval:: MAX_VM_FAILS

   Number of attempts to launch a virtual machine before considering it
   an error.
   The default value is 3.

.. confval:: VM_INFO_UPDATE_FREQUENCY

   Maximum frequency to update the VM info (in secs)
   The default value is 10.
   
.. confval:: VM_INFO_UPDATE_ERROR_GRACE_PERIOD

   Maximum time that a VM status maintains the current status in case of connection failure with the 
   Cloud provider (in secs). If the time is over this value the status is set to 'unknown'. 
   This value must be always higher than VM_INFO_UPDATE_FREQUENCY.
   The default value is 120.

.. confval:: WAIT_RUNNING_VM_TIMEOUT

   Timeout in seconds to get a virtual machine in running state.
   The default value is 1800.

.. confval:: WAIT_SSH_ACCCESS_TIMEOUT

   (**New in version IM version 1.5.1.**)
   Timeout in seconds to wait a virtual machine to get the SSH access active once it is in running state.
   The default value is 300.

.. confval:: LOG_FILE

   Full path to the log file.
   The default value is :file:`/var/log/im/inf.log`.

.. confval:: LOG_FILE_MAX_SIZE

   Maximum size in KiB of the log file before being rotated.
   The default value is 10485760.

.. _options-default-vm:

Default Virtual Machine Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. confval:: DEFAULT_VM_MEMORY 

   Default principal memory assigned to a virtual machine.
   The default value is 512.

.. confval:: DEFAULT_VM_MEMORY_UNIT 

   Unit used in :confval:`DEFAULT_VM_MEMORY`.
   Allowed values: ``K`` (KiB), ``M`` (MiB) and ``G`` (GiB).
   The default value is ``M``.

.. confval:: DEFAULT_VM_CPUS 

   Default number of CPUs assigned to a virtual machine.
   The default value is 1.

.. confval:: DEFAULT_VM_CPU_ARCH 

   Default CPU architecture assigned to a virtual machine.
   Allowed values: ``i386`` and ``x86_64``.
   The default value is ``x86_64``.

.. confval:: DEFAULT_VM_NAME 

   Default name of virtual machines.
   The default value is ``vnode-#N#``.

.. confval:: DEFAULT_DOMAIN 

   Default domain assigned to a virtual machine.
   The default value is ``localdomain``.

.. _options-ctxt:

Contextualization
^^^^^^^^^^^^^^^^^

.. confval:: CONTEXTUALIZATION_DIR

   Full path to the IM contextualization files.
   The default value is :file:`/usr/share/im/contextualization`.

.. confval:: RECIPES_DIR 

   Full path to the Ansible recipes directory.
   The default value is :file:`CONTEXTUALIZATION_DIR/AnsibleRecipes`.

.. confval:: RECIPES_DB_FILE 

   Full path to the Ansible recipes database file.
   The default value is :file:`CONTEXTUALIZATION_DIR/recipes_ansible.db`.

.. confval:: MAX_CONTEXTUALIZATION_TIME 

   Maximum time in seconds spent on contextualize a virtual machine before
   throwing an error.
   The default value is 7200.
   
.. confval:: REMOTE_CONF_DIR 

   Directory to copy all the ansible related files used in the contextualization.
   The default value is :file:`/tmp/.im`.
   
.. confval:: PLAYBOOK_RETRIES 

   Number of retries of the Ansible playbooks in case of failure.
   The default value is 1.
   
.. confval:: CHECK_CTXT_PROCESS_INTERVAL

   Interval to update the state of the contextualization process in the VMs (in secs).
   Reducing this time the load of the IM service will decrease in contextualization steps,
   but may introduce some overhead time. 
   The default value is 5.

.. confval:: CONFMAMAGER_CHECK_STATE_INTERVAL
   
   Interval to update the state of the processes of the ConfManager (in secs).
   Reducing this time the load of the IM service will decrease in contextualization steps,
   but may introduce some overhead time.
   The default value is 5.

.. confval:: UPDATE_CTXT_LOG_INTERVAL

   Interval to update the log output of the contextualization process in the VMs (in secs).
   The default value is 20.

.. _options-xmlrpc:

XML-RPC API
^^^^^^^^^^^

.. confval:: XMLRCP_PORT

   Port number where IM XML-RPC API is available.
   The default value is 8899.
   
.. confval:: XMLRCP_ADDRESS

   IP address where IM XML-RPC API is available.
   The default value is 0.0.0.0 (all the IPs).

.. confval:: XMLRCP_SSL 

   If ``True`` the XML-RPC API is secured with SSL certificates.
   The default value is ``False``.

.. confval:: XMLRCP_SSL_KEYFILE 

   Full path to the private key associated to the SSL certificate to access
   the XML-RPC API.
   The default value is :file:`/etc/im/pki/server-key.pem`.

.. confval:: XMLRCP_SSL_CERTFILE 

   Full path to the public key associated to the SSL certificate to access
   the XML-RPC API.
   The default value is :file:`/etc/im/pki/server-cert.pem`.

.. confval:: XMLRCP_SSL_CA_CERTS 

   Full path to the SSL Certification Authorities (CA) certificate.
   The default value is :file:`/etc/im/pki/ca-chain.pem`.

.. confval:: VMINFO_JSON

	Return the VM information of function GetVMInfo in RADL JSON instead of plain RADL
	(**Added in IM version 1.5.2**) 
	The default value is ``False``.

.. _options-rest:

REST API
^^^^^^^^

.. confval:: ACTIVATE_REST 

   If ``True`` the REST API is activated.
   The default value is ``False``.

.. confval:: REST_PORT

   Port number where REST API is available.
   The default value is 8800.
   
.. confval:: REST_ADDRESS

   IP address where REST API is available.
   The default value is 0.0.0.0 (all the IPs).

.. confval:: REST_SSL 

   If ``True`` the REST API is secured with SSL certificates.
   The default value is ``False``.

.. confval:: REST_SSL_KEYFILE 

   Full path to the private key associated to the SSL certificate to access
   the REST API.
   The default value is :file:`/etc/im/pki/server-key.pem`.

.. confval:: REST_SSL_CERTFILE 

   Full path to the public key associated to the SSL certificate to access
   the REST API.
   The default value is :file:`/etc/im/pki/server-cert.pem`.

.. confval:: REST_SSL_CA_CERTS 

   Full path to the SSL Certification Authorities (CA) certificate.
   The default value is :file:`/etc/im/pki/ca-chain.pem`.

.. _options-ganglia:

GANGLIA INTEGRATION
^^^^^^^^^^^^^^^^^^^

.. confval:: GET_GANGLIA_INFO 

   Flag to enable the retrieval of the ganglia info of the VMs.
   The default value is ``False``.
   
.. confval:: GANGLIA_INFO_UPDATE_FREQUENCY 

   Maximum frequency to update the Ganglia info (in secs).
   The default value is ``30``.

NETWORK OPTIONS
^^^^^^^^^^^^^^^

.. confval:: PRIVATE_NET_MASKS 

   List of networks assumed as private. The IM use it to distinguish private from public networks.
   IM considers IPs not in these subnets as Public IPs.
   It must be a coma separated string of the network definitions (using CIDR) (without spaces).
   The default value is ``'10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,192.0.0.0/24,169.254.0.0/16,100.64.0.0/10,198.18.0.0/15'``.
   
HA MODE OPTIONS
^^^^^^^^^^^^^^^

.. confval:: INF_CACHE_TIME

   Time (in seconds) the IM service will maintain the information of an infrastructure
   in memory. Only used in case of IM in HA mode. This value has to be set to a similar value set in the ``expire`` value
   in the ``stick-table`` in the HAProxy configuration.

OpenNebula connector Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration values under the ``OpenNebula`` section:

.. confval:: TEMPLATE_CONTEXT 

   Text to add to the CONTEXT section of the ONE template (except SSH_PUBLIC_KEY)
   The default value is ``''``.

.. confval:: TEMPLATE_OTHER 

   Text to add to the ONE Template different to NAME, CPU, VCPU, MEMORY, OS, DISK and CONTEXT
   The default value is ``GRAPHICS = [type="vnc",listen="0.0.0.0"]``. 


Docker Image
============

A Docker image named `grycap/im` has been created to make easier the deployment of an IM service using the 
default configuration. Information about this image can be found here: https://registry.hub.docker.com/u/grycap/im/.

How to launch the IM service using docker::

  $ sudo docker run -d -p 8899:8899 --name im grycap/im

You can also specify an external MySQL server to store IM data using the IM_DATA_DB environment variable::
  
  $ sudo docker run -d -p 8899:8899 -e IM_DATA_DB=mysql://username:password@server/db_name --name im grycap/im 

Or you can also add a volume with all the IM configuration::

  $ sudo docker run -d -p 8899:8899 -p 8800:8800 -v "/some_local_path/im.cfg:/etc/im/im.cfg" --name im grycap/im

.. _options-ha:

IM in high availability mode
============================

From version 1.5.0 the IM service can be launched in high availability (HA) mode using a set of IM instances
behind a `HAProxy <http://www.haproxy.org/>`_ load balancer. Currently only the REST API can be used in HA mode.
It is a experimental issue currently it is not intended to be used in a production installation.

This is an example of the HAProxy configuration file::

	frontend http-frontend
	    mode http
	    bind *:8800
	    default_backend imbackend
	
	backend imbackend
	    mode http
	    balance roundrobin
	    stick-table type string len 32 size 30k expire 60m
	    stick store-response hdr(InfID)
	    acl inf_id path -m beg /infrastructures/
	    stick on path,field(3,/) if inf_id

        server im-8801 10.0.0.1:8801 check
        server im-8802 10.0.0.1:8802 check
        ...

See more details of HAProxy configuration at `HAProxy Documentation <https://cbonte.github.io/haproxy-dconv/>`_.