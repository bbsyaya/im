#! /usr/bin/env python
#
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

import unittest
import xmlrpclib
import time

from IM.auth import Authentication
from IM.VirtualMachine import VirtualMachine
from IM.radl import radl_parse

RADL_ADD_WIN = "network publica\nnetwork privada\nsystem windows\ndeploy windows 1 one"
RADL_ADD = "network publica\nnetwork privada\nsystem wn\ndeploy wn 1 one"
RADL_ADD_ERROR = "system wnno deploy wnno 1"
TESTS_PATH = '/home/micafer/codigo/git_im/im/test'
RADL_FILE = TESTS_PATH + '/test.radl'
#RADL_FILE =  TESTS_PATH + '/test_ec2.radl'
AUTH_FILE = TESTS_PATH + '/auth.dat'
HOSTNAME = "localhost"
TEST_PORT = 8899

class TestIM(unittest.TestCase):

    server = None
    auth_data = None
    inf_id = 0

    @classmethod
    def setUpClass(cls):
        cls.server = xmlrpclib.ServerProxy("http://" + HOSTNAME + ":" + str(TEST_PORT),allow_none=True)
        cls.auth_data = Authentication.read_auth_data(AUTH_FILE)
        cls.inf_id = 0

    @classmethod
    def tearDownClass(cls):
        # Assure that the infrastructure is destroyed
        try:
            cls.server.DestroyInfrastructure(cls.inf_id, cls.auth_data)
        except Exception:
            pass

    def wait_inf_state(self, state, timeout, incorrect_states = [], vm_ids = None):
        """
        Wait for an infrastructure to have a specific state
        """
        if not vm_ids:
            (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
            self.assertTrue(success, msg="ERROR calling the GetInfrastructureInfo function:" + str(vm_ids))

        err_states = [VirtualMachine.FAILED, VirtualMachine.OFF, VirtualMachine.UNCONFIGURED]
        err_states.extend(incorrect_states)

        wait = 0
        all_ok = False
        while not all_ok and wait < timeout:
            all_ok = True
            for vm_id in vm_ids:
                (success, vm_state)  = self.server.GetVMProperty(self.inf_id, vm_id, "state", self.auth_data)
                self.assertTrue(success, msg="ERROR getting VM info:" + str(vm_state))

                if vm_state == VirtualMachine.UNCONFIGURED:
                    self.server.GetVMContMsg(self.inf_id, vm_id, self.auth_data)

                self.assertFalse(vm_state in err_states, msg="ERROR waiting for a state. '" + vm_state + "' was obtained in the VM: " + str(vm_id) + " err_states = " + str(err_states))
                
                if vm_state in err_states:
                    return False
                elif vm_state != state:
                    all_ok = False

            if not all_ok:
                wait += 5
                time.sleep(5)

        return all_ok

    def test_10_list(self):
        """
        Test the GetInfrastructureList IM function
        """
        (success, res) = self.server.GetInfrastructureList(self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureList: " + str(res))

    def test_11_create(self):
        """
        Test the CreateInfrastructure IM function
        """
        f = open(RADL_FILE)
        radl = ""
        for line in f.readlines():
            radl += line
        f.close()

        (success, inf_id) = self.server.CreateInfrastructure(radl, self.auth_data)
        self.assertTrue(success, msg="ERROR calling CreateInfrastructure: " + str(inf_id))
        self.__class__.inf_id = inf_id

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 900)
        self.assertTrue(all_configured, msg="ERROR waiting the infrastructure to be configured (timeout).")

    def test_12_getradl(self):
        """
        Test the GetInfrastructureRADL IM function
        """
        (success, res) = self.server.GetInfrastructureRADL(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureRADL: " + str(res))
        try:
            radl_parse.parse_radl(res)
        except Exception, ex:
            self.assertTrue(False, msg="ERROR parsing the RADL returned by GetInfrastructureRADL: " + str(ex))

    def test_13_getcontmsg(self):
        """
        Test the GetInfrastructureContMsg IM function
        """
        (success, cont_out) = self.server.GetInfrastructureContMsg(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureContMsg: " + str(cont_out))
        self.assertGreater(len(cont_out), 100, msg="Incorrect contextualization message: " + cont_out)
        
    def test_14_getvmcontmsg(self):
        """
        Test the GetVMContMsg IM function
        """
        (success, res) = self.server.GetVMContMsg(self.inf_id, 0, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetVMContMsg: " + str(res))
        self.assertGreater(len(res), 100, msg="Incorrect VM contextualization message: " + res)

    def test_15_get_vm_info(self):
        """
        Test the GetVMInfo IM function
        """
        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo: " + str(vm_ids))
        (success, info)  = self.server.GetVMInfo(self.inf_id, vm_ids[0], self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetVMInfo: " + str(info))
        try:
            radl_parse.parse_radl(info)
        except Exception, ex:
            self.assertTrue(False, msg="ERROR parsing the RADL returned by GetVMInfo: " + str(ex))       
            
    def test_16_get_vm_property(self):
        """
        Test the GetVMProperty IM function
        """
        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo: " + str(vm_ids))
        (success, info)  = self.server.GetVMProperty(self.inf_id, vm_ids[0], "state", self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetVMProperty: " + str(info))
        self.assertNotEqual(info, None, msg="ERROR in the value returned by GetVMProperty: " + info)
        self.assertNotEqual(info, "", msg="ERROR in the value returned by GetVMPropert: " + info)    

#     def test_17_get_ganglia_info(self):
#         """
#         Test the Ganglia IM information integration
#         """
#         (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
#         self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo: " + str(vm_ids))
#         (success, info)  = self.server.GetVMInfo(self.inf_id, vm_ids[1], self.auth_data)
#         self.assertTrue(success, msg="ERROR calling GetVMInfo: " + str(info))
#         info_radl = radl_parse.parse_radl(info)
#         prop_usage = info_radl.systems[0].getValue("cpu.usage")
#         self.assertIsNotNone(prop_usage, msg="ERROR getting ganglia VM info (cpu.usage = None) of VM " + str(vm_ids[1]))

    def test_18_error_addresource(self):
        """
        Test to get error when adding a resource with an incorrect RADL
        """
        (success, res) = self.server.AddResource(self.inf_id, RADL_ADD_ERROR, self.auth_data)
        self.assertFalse(success, msg="Incorrect RADL in AddResource not returned error")
        pos = res.find("Unknown reference in RADL")
        self.assertGreater(pos, -1, msg="Incorrect RADL in AddResource not returned the expected error: " + res)

    def test_19_addresource(self):
        """
        Test AddResource function
        """
        (success, res) = self.server.AddResource(self.inf_id, RADL_ADD_WIN, self.auth_data)
        self.assertTrue(success, msg="ERROR calling AddResource: " + str(res))

        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo:" + str(vm_ids))
        self.assertEqual(len(vm_ids), 4, msg="ERROR getting infrastructure info: Incorrect number of VMs(" + str(len(vm_ids)) + "). It must be 3")

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 900)
        self.assertTrue(all_configured, msg="ERROR waiting the infrastructure to be configured (timeout).")

    def test_20_addresource_noconfig(self):
        """
        Test AddResource function with the contex option to False
        """
        (success, res) = self.server.AddResource(self.inf_id, RADL_ADD, self.auth_data, False)
        self.assertTrue(success, msg="ERROR calling AddResource: " + str(res))

        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo:" + str(vm_ids))
        self.assertEqual(len(vm_ids), 5, msg="ERROR getting infrastructure info: Incorrect number of VMs(" + str(len(vm_ids)) + "). It must be 3")

    def test_21_removeresource(self):
        """
        Test RemoveResource function
        """
        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo: " + str(vm_ids))

        (success, res) = self.server.RemoveResource(self.inf_id, vm_ids[2], self.auth_data)
        self.assertTrue(success, msg="ERROR calling RemoveResource: " + str(res))

        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo:" + str(vm_ids))
        self.assertEqual(len(vm_ids), 4, msg="ERROR getting infrastructure info: Incorrect number of VMs(" + str(len(vm_ids)) + "). It must be 2")

        (success, vm_state)  = self.server.GetVMProperty(self.inf_id, vm_ids[0], "state", self.auth_data)
        self.assertTrue(success, msg="ERROR getting VM state:" + str(res))
        self.assertEqual(vm_state, VirtualMachine.RUNNING, msg="ERROR unexpected state. Expected 'running' and obtained " + vm_state)

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 600)
        self.assertTrue(all_configured, msg="ERROR waiting the infrastructure to be configured (timeout).")

    def test_22_removeresource_noconfig(self):
        """
        Test RemoveResource function with the context option to False
        """
        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo: " + str(vm_ids))

        (success, res) = self.server.RemoveResource(self.inf_id, vm_ids[2], self.auth_data, False)
        self.assertTrue(success, msg="ERROR calling RemoveResource: " + str(res))

        (success, vm_ids) = self.server.GetInfrastructureInfo(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureInfo:" + str(vm_ids))
        self.assertEqual(len(vm_ids), 3, msg="ERROR getting infrastructure info: Incorrect number of VMs(" + str(len(vm_ids)) + "). It must be 2")

        (success, vm_state)  = self.server.GetVMProperty(self.inf_id, vm_ids[0], "state", self.auth_data)
        self.assertTrue(success, msg="ERROR getting VM state:" + str(res))
        self.assertEqual(vm_state, VirtualMachine.CONFIGURED, msg="ERROR unexpected state. Expected 'running' and obtained " + vm_state)

    def test_23_reconfigure(self):
        """
        Test Reconfigure function
        """
        (success, res) = self.server.Reconfigure(self.inf_id, "", self.auth_data)
        self.assertTrue(success, msg="ERROR calling Reconfigure: " + str(res))

        all_stopped = self.wait_inf_state(VirtualMachine.CONFIGURED, 600)
        self.assertTrue(all_stopped, msg="ERROR waiting the infrastructure to be configured (timeout).")
        
    def test_24_reconfigure_vmlist(self):
        """
        Test Reconfigure function specifying a list of VMs
        """
        (success, res) = self.server.Reconfigure(self.inf_id, "", self.auth_data, [0])
        self.assertTrue(success, msg="ERROR calling Reconfigure: " + str(res))

        all_stopped = self.wait_inf_state(VirtualMachine.CONFIGURED, 600)
        self.assertTrue(all_stopped, msg="ERROR waiting the infrastructure to be configured (timeout).")
        
    def test_25_reconfigure_radl(self):
        """
        Test Reconfigure function specifying a new RADL
        """
        radl = """configure test (\n@begin\n---\n  - tasks:\n      - debug: msg="RECONFIGURERADL"\n@end\n)"""
        (success, res) = self.server.Reconfigure(self.inf_id, radl, self.auth_data)
        self.assertTrue(success, msg="ERROR calling Reconfigure: " + str(res))

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 600)
        self.assertTrue(all_configured, msg="ERROR waiting the infrastructure to be configured (timeout).")
        
        (success, cont_out) = self.server.GetInfrastructureContMsg(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling GetInfrastructureContMsg: " + str(cont_out))
        self.assertIn("RECONFIGURERADL", cont_out, msg="Incorrect contextualization message: " + cont_out)

    def test_30_stop(self):
        """
        Test StopInfrastructure function
        """
        (success, res) = self.server.StopInfrastructure(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling StopInfrastructure: " + str(res))

        all_stopped = self.wait_inf_state(VirtualMachine.STOPPED, 120, [VirtualMachine.RUNNING])
        self.assertTrue(all_stopped, msg="ERROR waiting the infrastructure to be stopped (timeout).")

    def test_31_start(self):
        """
        Test StartInfrastructure function
        """
        # Assure the VM to be stopped
        time.sleep(10)
        (success, res) = self.server.StartInfrastructure(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling StartInfrastructure: " + str(res))

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 150, [VirtualMachine.RUNNING])
        self.assertTrue(all_configured, msg="ERROR waiting the infrastructure to be started (timeout).")

    def test_32_stop_vm(self):
        """
        Test StopVM function
        """
        (success, res) = self.server.StopVM(self.inf_id, 0, self.auth_data)
        self.assertTrue(success, msg="ERROR calling StopVM: " + str(res))

        all_stopped = self.wait_inf_state(VirtualMachine.STOPPED, 120, [VirtualMachine.RUNNING], [0])
        self.assertTrue(all_stopped, msg="ERROR waiting the vm to be stopped (timeout).")
        
    def test_33_start_vm(self):
        """
        Test StartVM function
        """
        # Assure the VM to be stopped
        time.sleep(10)
        (success, res) = self.server.StartVM(self.inf_id, 0, self.auth_data)
        self.assertTrue(success, msg="ERROR calling StartVM: " + str(res))

        all_configured = self.wait_inf_state(VirtualMachine.CONFIGURED, 150, [VirtualMachine.RUNNING], [0])
        self.assertTrue(all_configured, msg="ERROR waiting the vm to be started (timeout).")

    def test_40_export_import(self):
        """
        Test ExportInfrastructure and ImportInfrastructure functions
        """
        (success, res) = self.server.ExportInfrastructure(self.inf_id, False, self.auth_data)
        self.assertTrue(success, msg="ERROR calling ExportInfrastructure: " + str(res))
        
        (success, res) = self.server.ImportInfrastructure(res, self.auth_data)
        self.assertTrue(success, msg="ERROR calling ImportInfrastructure: " + str(res))

        self.assertEqual(res, self.inf_id+1, msg="ERROR importing the inf.")

    def test_50_destroy(self):
        """
        Test DestroyInfrastructure function
        """
        (success, res) = self.server.DestroyInfrastructure(self.inf_id, self.auth_data)
        self.assertTrue(success, msg="ERROR calling DestroyInfrastructure: " + str(res))

if __name__ == '__main__':
    unittest.main()
