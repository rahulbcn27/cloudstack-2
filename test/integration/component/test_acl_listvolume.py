# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Test cases relating to listVolumes() relating to parameters - id,listall,isrecursive,account and domainid
"""
# Import Local Modules
import marvin
from marvin.cloudstackTestCase import *
from marvin.cloudstackAPI import *
from marvin.lib.utils import *
from marvin.lib.base import *
from marvin.lib.common import *
from nose.plugins.attrib import attr
# Import System modules
import time

_multiprocess_shared_ = True


class TestVolumeList(cloudstackTestCase):
    @classmethod
    def setUpClass(cls):
        """
            Create the following domain tree and accounts that are reqiured for executing listVolume test cases:
            Under ROOT - create 2 domaind D1 and D2
            Under D1 - Create 2 subdomain D11 and D12
            Under D11 - Create subdimain D111

            Under each of the domain create 1 admin user and couple of regular users.

            As each of these users , deploy Virtual machines.

        """
        cls.testclient = super(TestVolumeList, cls).getClsTestClient()
        cls.apiclient = cls.testclient.getApiClient()
        cls.testdata = cls.testClient.getParsedTestDataConfig()
        cls.acldata = cls.testdata["acl"]

        cls.domain_1 = None
        cls.domain_2 = None
        cls.cleanup = []

        try:

            # backup default apikey and secretkey
            cls.default_apikey = cls.apiclient.connection.apiKey
            cls.default_secretkey = cls.apiclient.connection.securityKey

            # Create domains
            cls.domain_1 = Domain.create(
                cls.apiclient,
                cls.acldata["domain1"]
            )
            cls.domain_11 = Domain.create(
                cls.apiclient,
                cls.acldata["domain11"],
                parentdomainid=cls.domain_1.id
            )
            cls.domain_111 = Domain.create(
                cls.apiclient,
                cls.acldata["domain111"],
                parentdomainid=cls.domain_11.id,
            )
            cls.domain_12 = Domain.create(
                cls.apiclient,
                cls.acldata["domain12"],
                parentdomainid=cls.domain_1.id
            )
            cls.domain_2 = Domain.create(
                cls.apiclient,
                cls.acldata["domain2"]
            )
            # Create  1 admin account and 2 user accounts for doamin_1
            cls.account_d1 = Account.create(
                cls.apiclient,
                cls.acldata["accountD1"],
                admin=True,
                domainid=cls.domain_1.id
            )

            user = cls.generateKeysForUser(cls.apiclient, cls.account_d1)
            cls.user_d1_apikey = user.apikey
            cls.user_d1_secretkey = user.secretkey

            cls.account_d1a = Account.create(
                cls.apiclient,
                cls.acldata["accountD1A"],
                admin=False,
                domainid=cls.domain_1.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d1a)
            cls.user_d1a_apikey = user.apikey
            cls.user_d1a_secretkey = user.secretkey

            cls.account_d1b = Account.create(
                cls.apiclient,
                cls.acldata["accountD1B"],
                admin=False,
                domainid=cls.domain_1.id
            )

            user = cls.generateKeysForUser(cls.apiclient, cls.account_d1b)
            cls.user_d1b_apikey = user.apikey
            cls.user_d1b_secretkey = user.secretkey

            # Create  1 admin and 2 user accounts for doamin_11
            cls.account_d11 = Account.create(
                cls.apiclient,
                cls.acldata["accountD11"],
                admin=True,
                domainid=cls.domain_11.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d11)
            cls.user_d11_apikey = user.apikey
            cls.user_d11_secretkey = user.secretkey

            cls.account_d11a = Account.create(
                cls.apiclient,
                cls.acldata["accountD11A"],
                admin=False,
                domainid=cls.domain_11.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d11a)
            cls.user_d11a_apikey = user.apikey
            cls.user_d11a_secretkey = user.secretkey

            cls.account_d11b = Account.create(
                cls.apiclient,
                cls.acldata["accountD11B"],
                admin=False,
                domainid=cls.domain_11.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d11b)
            cls.user_d11b_apikey = user.apikey
            cls.user_d11b_secretkey = user.secretkey

            # Create  1 user account for doamin_111

            cls.account_d111a = Account.create(
                cls.apiclient,
                cls.acldata["accountD111A"],
                admin=False,
                domainid=cls.domain_111.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d111a)
            cls.user_d111a_apikey = user.apikey
            cls.user_d111a_secretkey = user.secretkey

            # Create  2 user accounts for doamin_12
            cls.account_d12a = Account.create(
                cls.apiclient,
                cls.acldata["accountD12A"],
                admin=False,
                domainid=cls.domain_12.id
            )
            user = cls.generateKeysForUser(cls.apiclient, cls.account_d12a)
            cls.user_d12a_apikey = user.apikey
            cls.user_d12a_secretkey = user.secretkey

            cls.account_d12b = Account.create(
                cls.apiclient,
                cls.acldata["accountD12B"],
                admin=False,
                domainid=cls.domain_12.id
            )

            user = cls.generateKeysForUser(cls.apiclient, cls.account_d12b)
            cls.user_d12b_apikey = user.apikey
            cls.user_d12b_secretkey = user.secretkey

            # Create 1 user account for domain_2

            cls.account_d2a = Account.create(
                cls.apiclient,
                cls.acldata["accountD2"],
                admin=False,
                domainid=cls.domain_2.id
            )

            user = cls.generateKeysForUser(cls.apiclient, cls.account_d2a)
            cls.user_d2a_apikey = user.apikey
            cls.user_d2a_secretkey = user.secretkey

            # Create admin user account

            cls.account_a = Account.create(
                cls.apiclient,
                cls.acldata["accountROOTA"],
                admin=True,
            )

            user = cls.generateKeysForUser(cls.apiclient, cls.account_a)
            cls.user_a_apikey = user.apikey
            cls.user_a_secretkey = user.secretkey
            # create service offering
            cls.service_offering = ServiceOffering.create(
                cls.apiclient,
                cls.acldata["service_offering"]["small"]
            )

            cls.zone = get_zone(cls.apiclient, cls.testclient.getZoneForTests())
            cls.acldata['mode'] = cls.zone.networktype
            cls.template = get_template(cls.apiclient, cls.zone.id, cls.acldata["ostype"])

            # deploy VM

            cls.apiclient.connection.apiKey = cls.user_d1_apikey
            cls.apiclient.connection.securityKey = cls.user_d1_secretkey
            cls.vm_d1 = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD1"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d1_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d1.id)

            cls.apiclient.connection.apiKey = cls.user_d1a_apikey
            cls.apiclient.connection.securityKey = cls.user_d1a_secretkey
            cls.vm_d1a = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD1A"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d1a_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d1a.id)

            cls.apiclient.connection.apiKey = cls.user_d1b_apikey
            cls.apiclient.connection.securityKey = cls.user_d1b_secretkey
            cls.vm_d1b = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD1B"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d1b_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d1b.id)

            cls.apiclient.connection.apiKey = cls.user_d11_apikey
            cls.apiclient.connection.securityKey = cls.user_d11_secretkey
            cls.vm_d11 = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD11"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d11_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d11.id)

            cls.apiclient.connection.apiKey = cls.user_d11a_apikey
            cls.apiclient.connection.securityKey = cls.user_d11a_secretkey
            cls.vm_d11a = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD11A"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d11a_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d11a.id)

            cls.apiclient.connection.apiKey = cls.user_d11b_apikey
            cls.apiclient.connection.securityKey = cls.user_d11b_secretkey
            cls.vm_d11b = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD11B"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d11b_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d11b.id)

            cls.apiclient.connection.apiKey = cls.user_d111a_apikey
            cls.apiclient.connection.securityKey = cls.user_d111a_secretkey
            cls.vm_d111a = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD111A"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d111a_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d111a.id)

            cls.apiclient.connection.apiKey = cls.user_d12a_apikey
            cls.apiclient.connection.securityKey = cls.user_d12a_secretkey
            cls.vm_d12a = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD12A"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d12a_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d12a.id)

            cls.apiclient.connection.apiKey = cls.user_d12b_apikey
            cls.apiclient.connection.securityKey = cls.user_d12b_secretkey
            cls.vm_d12b = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD12B"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d12b_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d12b.id)

            cls.apiclient.connection.apiKey = cls.user_d2a_apikey
            cls.apiclient.connection.securityKey = cls.user_d2a_secretkey
            cls.vm_d2 = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmD2A"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_d2_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_d2.id)

            cls.apiclient.connection.apiKey = cls.user_a_apikey
            cls.apiclient.connection.securityKey = cls.user_a_secretkey
            cls.vm_a = VirtualMachine.create(
                cls.apiclient,
                cls.acldata["vmROOTA"],
                zoneid=cls.zone.id,
                serviceofferingid=cls.service_offering.id,
                templateid=cls.template.id
            )
            cls.vm_a_volume = Volume.list(cls.apiclient, virtualmachineid=cls.vm_a.id)

            cls.cleanup = [
                cls.account_a,
                cls.service_offering,
            ]
        except Exception as e:
            cls.domain_2.delete(cls.apiclient, cleanup="true")
            cls.domain_1.delete(cls.apiclient, cleanup="true")
            cleanup_resources(cls.apiclient, cls.cleanup)
            raise Exception("Failed to create the setup required to execute the test cases: %s" % e)

    @classmethod
    def tearDownClass(cls):
        cls.apiclient = super(TestVolumeList, cls).getClsTestClient().getApiClient()
        cls.apiclient.connection.apiKey = cls.default_apikey
        cls.apiclient.connection.securityKey = cls.default_secretkey
        cleanup_resources(cls.apiclient, cls.cleanup)
        try:
            cls.domain_2.delete(cls.apiclient, cleanup="true")
            cls.domain_1.delete(cls.apiclient, cleanup="true")
        except:
            pass

    def setUp(cls):
        cls.apiclient = cls.testClient.getApiClient()
        cls.dbclient = cls.testClient.getDbConnection()

    def tearDown(cls):
        # restore back default apikey and secretkey
        cls.apiclient.connection.apiKey = cls.default_apikey
        cls.apiclient.connection.securityKey = cls.default_secretkey
        return

    ## Domain Admin - Test cases  with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_true(self):
        """
        # Test listing of Volumes by passing listall="true" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by accounts in this domain and all its subdomain
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="true")
        self.debug("List as Domain Admin - listall=true -  %s" % volumeList)

        self.assertEqual(len(volumeList) == 9,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing listall="true"i and isrecusriv="true" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by accounts in this domain and all its subdomain
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="true")
        self.debug("List as Domain Admin  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 9,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing listall="true" and isrecusriv="false" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by accounts in this domain and all its subdomain
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="false")
        self.debug("List as Domain Admin  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 9,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_false(self):
        """
        # Test listing of Volumes by passing listall="false" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="false")
        self.debug("List as Domain Admin - listall=false -  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="true" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="true")
        self.debug("List as Domain Admin  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="false" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="false")
        self.debug("List as Domain Admin  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")
        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  without passing listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin(self):
        """
        # Test listing of Volumes by passing no parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient)
        self.debug("List as Domain Admin - %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_rec_true(self):
        """
        # Test listing of Volumes by passing isrecusrive="true" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="true")
        self.debug("List as Domain Admin  - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_true_rec_false(self):
        """
        # Test listing of Volumes by passing isrecusrive="false" parameter as domain admin
        # Validate that it returns all the Volumes that is owned by the domain admin
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="false")
        self.debug("List as Domain Admin  - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases when domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_true(self):
        """
        # Test listing of Volumes by passing domainId and listall="true" parameter as domain admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true")
        self.debug("List as Domain Admin passing domainId  - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainId ,listall="true" and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes in the subdomain and the domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true", isrecursive="true")
        self.debug("List as Domain Admin passing domainId  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing domainId ,listall="true" and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true", isrecursive="false")
        self.debug("List as Domain Admin passing domainId  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  when domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_false(self):
        # Test listing of Volumes by passing domainId ,listall="false" parameter as domain admin
        # Validate that it returns all the Volumes in the domain passed

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false")
        self.debug("List as Domain Admin passing domainId  - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing domainId ,listall="false" and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes in the subdomain and the domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false", isrecursive="true")
        self.debug("List as Domain Admin passing domainId  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing domainId ,listall="false" and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false", isrecursive="false")
        self.debug("List as Domain Admin passing domainId  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  when domainId is passed with no listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid(self):
        """
        # Test listing of Volumes by passing domainId parameter as domain admin
        # Validate that it returns all the Volumes in the domain passed
        """
        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id)
        self.debug("List as Domain Admin passing domainId  - %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_rec_true(self):
        """
        # Test listing of Volumes by passing domainId and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes in the subdomain and domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, isrecursive="true")
        self.debug("List as Domain Admin passing domainId  - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_rec_false(self):
        """
        # Test listing of Volumes by passing domainId and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes in the subdomain and domain passed
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, isrecursive="false")
        self.debug("List as Domain Admin passing domainId  - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  when account and domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_true(self):
        """
        # Test listing of Volumes by passing account ,domainId and listall="true" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true")
        self.debug("List as Domain Admin passing domainId and accountId - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing account ,domainId and listall="true" and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true", isrecursive="true")
        self.debug("List as Domain Admin passing domainId and accountId - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing account ,domainId , listall="true" and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true", isrecursive="false")
        self.debug("List as Domain Admin passing domainId and accountId - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  when account and domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_false(self):
        """
        # Test listing of Volumes by passing account ,domainId and listall="false" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false")
        self.debug("List as Domain Admin passing domainId and accountId - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing account ,domainId and listall="false" and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false", isrecursive="true")
        self.debug("List as Domain Admin passing domainId and accountId - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing account ,domainId , listall="false" and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false", isrecursive="false")
        self.debug("List as Domain Admin passing domainId and accountId - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Domain Admin - Test cases  when account and domainId is passed with listall not passed

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid(self):
        """
        # Test listing of Volumes by passing account ,domainId parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """
        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id)
        self.debug("List as Domain Admin passing domainId and accountId - %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_rec_true(self):
        """
        # Test listing of Volumes by passing account ,domainId and isrecursive="true" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, isrecursive="true")
        self.debug("List as Domain Admin passing domainId and accountId - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_domainid_accountid_rec_false(self):
        """
        # Test listing of Volumes by passing account ,domainId and isrecursive="false" parameter as domain admin
        # Validate that it returns all the Volumes owned by the account passed in account parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, isrecursive="false")
        self.debug("List as Domain Admin passing domainId and accountId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_true(self):
        """
        # Test listing of Volumes by passing listall="true" parameter as admin
        # Validate that it returns all the Volumes
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true")
        self.debug("List as ROOT Admin - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) >= 11,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d2_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id)):

            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing listall="true" and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="true")
        self.debug("List as ROOT Admin  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) >= 11,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d2_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id)):

            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing listall="true" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="false")
        self.debug("List as ROOT Admin  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) >= 11,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d1_volume[0].id),
            self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d1b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d12b_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_d2_volume[0].id) and
            self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_false(self):
        """
        # Test listing of Volumes by passing listall="false" parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false")
        self.debug("List as ROOT Admin - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="true")
        self.debug("List as ROOT Admin  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="false")
        self.debug("List as ROOT Admin  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  without passing listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin(self):
        """
        # Test listing of Volumes by passing no parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient)
        self.debug("List as ROOT Admin  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_rec_true(self):
        """
        # Test listing of Volumes by passing isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="true")
        self.debug("List as ROOT Admin - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_rec_false(self):
        """
        # Test listing of Volumes by passing isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes owned by admin
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="false")
        self.debug("List as ROOT Admin passing domainId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases when domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_true(self):
        """
        # Test listing of Volumes by passing domainid and listall="true" parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true")
        self.debug("List as ROOT Admin passing domainId  - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainid , listall="true" and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes in the subdomain and the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true", isrecursive="true")
        self.debug("List as ROOT Admin passing domainId  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing domainid, listall="true" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="true", isrecursive="false")
        self.debug("List as ROOT Admin passing domainId  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  when domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_false(self):
        """
        # Test listing of Volumes by passing domainid, listall="false" parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false")
        self.debug("List as ROOT Admin passing domainId  - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing domainid, listall="false" and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes in the subdomain and domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false", isrecursive="true")
        self.debug("List as ROOT Admin passing domainId  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing domainid, listall="false" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, listall="false", isrecursive="false")
        self.debug("List as ROOT Admin passing domainId  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  when domainId is passed with no listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid(self):
        """
        # Test listing of Volumes by passing domainid parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id)
        self.debug("List as ROOT Admin passing domainId  - %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_rec_true(self):
        """
        # Test listing of Volumes by passing domainid and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes in the subdmain and domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, isrecursive="true")
        self.debug("List as ROOT Admin passing domainId  - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 4,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d111a_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_rec_false(self):
        """
        # Test listing of Volumes by passing domainid and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes in the domain passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_11.id, isrecursive="false")
        self.debug("List as ROOT Admin passing domainId  - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 3,
                         True,
                         "Number of items in list response check failed!!")

        if (self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11a_volume[0].id) and
                self.checkForExistenceOfValue(volumeList, self.vm_d11b_volume[0].id)):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  when account and domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_true(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "true" parameter as admin
        # Validate that it returns all the Volumes of account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "true" and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true", isrecursive="true")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "true" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="true", isrecursive="false")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  when account and domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_false(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "false" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "false" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false", isrecursive="true")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account ,listall = "false" and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, listall="false", isrecursive="false")
        self.debug("List as ROOT Admin passing domainId and accountId - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## ROOT Admin - Test cases  when account and domainId is passed with listall not passed

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid(self):
        """
        # Test listing of Volumes by passing domainid,account parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id)
        self.debug("List as ROOT Admin passing domainId and accountId -  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,account and isrecusrive="true" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, isrecursive="true")
        self.debug("List as ROOT Admin passing domainId and accountId - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_rootadmin_domainid_accountid_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account and isrecusrive="false" parameter as admin
        # Validate that it returns all the Volumes of the account that is passed
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d11.user[0].username, domainid=self.domain_11.id, isrecursive="false")
        self.debug("List as ROOT Admin passing domainId and accountId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d11_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Regular User - Test cases  with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_true(self):
        """
        # Test listing of Volumes by passing listall="true"  parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true")
        self.debug("List as Regular User - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing listall="true" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="true")
        self.debug("List as Regular User  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing listall="true" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="true", isrecursive="false")
        self.debug("List as Regular User  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_false(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false")
        self.debug("List as Regular User - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="true")
        self.debug("List as Regular User  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing listall="false" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, listall="false", isrecursive="false")
        self.debug("List as Regular User  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  without passing listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser(self):
        """
        # Test listing of Volumes by passing no parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient)
        self.debug("List as Regular User  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_rec_true(self):
        """
        # Test listing of Volumes by passing isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="true")
        self.debug("List as Regular User - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_rec_false(self):
        """
        # Test listing of Volumes by passing isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, isrecursive="false")
        self.debug("List as Regular User passing domainId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases when domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_true(self):
        """
        # Test listing of Volumes by passing domainid,listall="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="true")
        self.debug("List as Regular User passing domainId  - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,listall="true" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="true", isrecursive="true")
        self.debug("List as Regular User passing domainId  - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,listall="true" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="true", isrecursive="false")
        self.debug("List as Regular User passing domainId  - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  when domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_false(self):
        """
        # Test listing of Volumes by passing domainid,listall="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="false")
        self.debug("List as Regular User passing domainId  - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_false_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,listall="false" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="false", isrecursive="true")
        self.debug("List as Regular User passing domainId  - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,listall="false" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, listall="false", isrecursive="false")
        self.debug("List as Regular User passing domainId  - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  when domainId is passed with no listall parameter

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid(self):
        """
        # Test listing of Volumes by passing domainid parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id)
        self.debug("List as Regular User passing domainId  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainid and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, isrecursive="true")
        self.debug("List as Regular User passing domainId - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid__rec_false(self):
        """
        # Test listing of Volumes by passing domainid,isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, domainid=self.domain_1.id, isrecursive="false")
        self.debug("List as Regular User passing domainId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  when account and domainId is passed with listall =true

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_true(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="true")
        self.debug("List as Regular User passing domainId and accountId - listall=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_true_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="true" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="true", isrecursive="true")
        self.debug("List as Regular User passing domainId and accountId - listall=true,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_true_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="true" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="true", isrecursive="false")
        self.debug("List as Regular User passing domainId and accountId - listall=true,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User - Test cases  when account and domainId is passed with listall=false

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_false(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="false")
        self.debug("List as Regular User passing domainId and accountId - listall=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_false_rec_true(self):
        # Test listing of Volumes by passing domainid,account,listall="false" and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="false", isrecursive="true")
        self.debug("List as Regular User passing domainId and accountId - listall=false,isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_listall_false_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account,listall="false" and isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, listall="false", isrecursive="false")
        self.debug("List as Regular User passing domainId and accountId - listall=false,isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ##  Regular User  - Test cases  when account and domainId is passed with listall not passed

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid(self):
        """
        # Test listing of Volumes by passing domainid,account parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id)
        self.debug("List as Regular User passing domainId and accountId  %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_rec_true(self):
        """
        # Test listing of Volumes by passing domainid,account and isrecusrive="true" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, isrecursive="true")
        self.debug("List as Regular User passing domainId and accountId - isrecursive=true %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_domainid_accountid_rec_false(self):
        """
        # Test listing of Volumes by passing domainid,account isrecusrive="false" parameter as regular user
        # Validate that it returns all the Volumes of the account the user belongs to
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        volumeList = Volume.list(self.apiclient, account=self.account_d1a.user[0].username, domainid=self.domain_1.id, isrecursive="false")
        self.debug("List as Regular User passing domainId and accountId - isrecursive=false %s" % volumeList)

        self.assertEqual(len(volumeList) == 1,
                         True,
                         "Number of items in list response check failed!!")

        if self.checkForExistenceOfValue(volumeList, self.vm_d1a_volume[0].id):
            accountAccess = True
        else:
            accountAccess = False

        self.assertEqual(accountAccess,
                         True,
                         "Account access check failed!!")

    ## Cross Domain access check

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_cross_domainid_accountid(self):
        """
        # Regular User should not be allowed to list Volumes of other accounts in the same domain
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        try:
            volumeList = Volume.list(self.apiclient, account=self.account_d1b.user[0].username, domainid=self.domain_1.id)
            self.fail("Regular User is able to use another account with in the same domain in listVolume call")
        except Exception as e:
            self.debug("List as Regular User passing domainId and accountId of another account %s" % e)

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_regularuser_cross_domainid(self):
        """
        # Regular User should not be allowed to list Volumes of other accounts in other domains
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        try:
            volumeList = Volume.list(self.apiclient, domainid=self.domain_2_volume[0].id)
            self.fail("Regular User is able to use another domain in listVolume call")
        except Exception as e:
            self.debug("List as Regular User passing domainId of a domain that user does not belong to %s" % e)

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_cross_domainid_accountid(self):
        """
        # Domain admin should not be allowed to list Volumes of accounts in other domains
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        try:
            volumeList = Volume.list(self.apiclient, account=self.account_d2a.user[0].username, domainid=self.domain_2_volume[0].id)
            self.fail("Domain admin user is able to use another domain in listVolume call")
        except Exception as e:
            self.debug("List as domain admin passing domainId and accountId of another account %s" % e)

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_as_domainadmin_cross_domainid(self):
        """
        # Domain admin should not be allowed to list Volumes from other domains
        """

        self.apiclient.connection.apiKey = self.user_d1a_apikey
        self.apiclient.connection.securityKey = self.user_d1a_secretkey
        try:
            volumeList = Volume.list(self.apiclient, domainid=self.domain_2_volume[0].id)
            self.fail("Domain admin User is able to use another domain in listVolume call")
        except Exception as e:
            self.debug("List as  domain admin passing domainId of a domain that user does not belong to %s" % e)

    ## List test cases relating to filter - id
    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_domainadmin_owns(self):
        """
        # Domain admin should be able to list Volumes that are self-owned by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        VMList = Volume.list(self.apiclient, id=self.vm_d1_volume[0].id)

        self.assertNotEqual(VMList,
                            None,
                            "Domain Admin is not able to list Volumes that are self-owned")

        self.assertEqual(len(VMList),
                         1,
                         "Domain Admin is not able to list Volumes that are self-owned")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_domainadmin_ownedbyusersindomain(self):
        """
        # Domain admin should be able to list Volumes that is  owned by any account in their domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        VMList1 = Volume.list(self.apiclient, id=self.vm_d1a_volume[0].id)

        self.assertNotEqual(VMList1,
                            None,
                            "Domain Admin is not able to list Volumes from their domain")

        self.assertEqual(len(VMList1),
                         1,
                         "Domain Admin is not able to list Volumes from their domain")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_domainadmin_ownedbyusersinsubdomain(self):
        """
        # Domain admin should be able to list Volumes that is  owned by any account in their sub-domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        VMList2 = Volume.list(self.apiclient, id=self.vm_d12b_volume[0].id)

        self.assertNotEqual(VMList2,
                            None,
                            "Domain Admin is not able to list Volumes from their sub domain")

        self.assertEqual(len(VMList2),
                         1,
                         "Domain Admin is not able to list Volumes from their sub domain")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_domainadmin_ownedbyusersnotindomain(self):
        """
        # Domain admin should not be able to list Volumes that is owned by account that is not in their domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        VMList3 = Volume.list(self.apiclient, id=self.vm_d2_volume[0].id)

        self.assertEqual(VMList3,
                         None,
                         "Domain Admin is able to list Volumes from  other domains!!!")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_domainadmin_ownedbyusersinsubdomain2(self):
        """
        # Domain admin should be able to list Volumes that is owned by account that is in their sub domains by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d1_apikey
        self.apiclient.connection.securityKey = self.user_d1_secretkey
        VMList4 = Volume.list(self.apiclient, id=self.vm_d111a_volume[0].id)

        self.assertNotEqual(VMList4,
                            None,
                            "Domain Admin is not able to list Volumes from their subdomain")

        self.assertEqual(len(VMList4),
                         1,
                         "Domain Admin is not able to list Volumes from their sub domains")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_rootadmin_owns(self):
        """
        # ROOT admin should be able to list Volumes that is owned by accounts  in their domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_a_apikey
        self.apiclient.connection.securityKey = self.user_a_secretkey
        VMList1 = Volume.list(self.apiclient, id=self.vm_a_volume[0].id)
        self.assertNotEqual(VMList1,
                            None,
                            "ROOT Admin not able to list Volumes that are self-owned")
        self.assertEqual(len(VMList1),
                         1,
                         "ROOT Admin not able to list Volumes that are self-owned")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_rootadmin_Volumesownedbyothers(self):
        """
        # ROOT admin should be able to list Volumes that is owned by any account by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.default_apikey
        self.apiclient.connection.securityKey = self.default_secretkey
        VMList1 = Volume.list(self.apiclient, id=self.vm_d2_volume[0].id)
        VMList2 = Volume.list(self.apiclient, id=self.vm_d11a_volume[0].id)
        self.assertNotEqual(VMList1,
                            None,
                            "ROOT Admin not able to list Volumes from other domains")

        self.assertNotEqual(VMList2,
                            None,
                            "ROOT Admin not able to list Volumes from other domains")
        self.assertEqual(len(VMList1),
                         1,
                         "ROOT Admin not able to list Volumes from other domains")
        self.assertEqual(len(VMList2),
                         1,
                         "ROOT Admin not able to list Volumes from other domains")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_user_own(self):
        """
        # Regular user should be able to list Volumes that are self-owned by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d11a_apikey
        self.apiclient.connection.securityKey = self.user_d11a_secretkey
        VMList1 = Volume.list(self.apiclient, id=self.vm_d11a_volume[0].id)

        self.assertNotEqual(VMList1,
                            None,
                            "Regular User is not able to list Volumes that are self-owned")

        self.assertEqual(len(VMList1),
                         1,
                         "Regular User is not able to list Volumes that are self-owned")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_user_volumefromsamedomaindifferentaccount(self):
        """
        # Regular user should not be able to list Volumes that is owned by different account in the same domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d11a_apikey
        self.apiclient.connection.securityKey = self.user_d11a_secretkey
        VMList2 = Volume.list(self.apiclient, id=self.vm_d11b_volume[0].id)

        self.assertEqual(VMList2,
                         None,
                         "Regular User  is able to list Volumes from  other accounts")

    @attr("simulator_only", tags=["advanced"], required_hardware="false")
    def test_listVolume_by_id_as_user_volumefromotherdomain(self):
        """
        # Regular user should not be able to list Volumes that is owned by different account in the different domain by passing uuid in "id" parameter
        """

        self.apiclient.connection.apiKey = self.user_d11a_apikey
        self.apiclient.connection.securityKey = self.user_d11a_secretkey
        VMList3 = Volume.list(self.apiclient, id=self.vm_d2_volume[0].id)

        self.assertEqual(VMList3,
                         None,
                         "Regular User  is able to list Volumes from  other domains")

    @staticmethod
    def generateKeysForUser(apiclient, account):
        user = User.list(
            apiclient,
            account=account.name,
            domainid=account.domainid
        )[0]

        return (User.registerUserKeys(
            apiclient,
            user.id
        ))

    @staticmethod
    def checkForExistenceOfValue(list, attributeValue):
        if list is None:
            return False
        rowCount = len(list)
        for num in range(rowCount):
            if list[num].id == attributeValue:
                return True
        return False
