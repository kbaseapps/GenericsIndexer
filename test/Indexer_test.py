# -*- coding: utf-8 -*-
import json  # noqa: F401
import os  # noqa: F401
import unittest
from configparser import ConfigParser  # py3
from os import environ
from unittest.mock import patch, Mock

from Utils.Indexer import Indexer
from installed_clients.WorkspaceClient import Workspace as workspaceService


class MiscIndexerTester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('GenericsIndexer'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        # authServiceUrl = cls.cfg['auth-service-url']
        # auth_client = _KBaseAuth(authServiceUrl)
        # user_id = auth_client.get_user(cls.token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.scratch = cls.cfg['scratch']
        cls.cfg['token'] = cls.token
        cls.upa = '1/2/3'
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.mock_dir = os.path.join(cls.test_dir, 'data')

        cls.amplicon_matrix = cls.read_mock('AmpliconMatrix.json')
        cls.attribute_mapping = cls.read_mock('AttributeMapping.json')
        cls.parsed_attribute_mapping = cls.read_mock('ParsedAttributeMapping.json')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @classmethod
    def read_mock(cls, filename):
        with open(os.path.join(cls.mock_dir, filename)) as f:
            obj = json.loads(f.read())
        return obj

    @patch('Utils.Indexer.WorkspaceAdminUtils', autospec=True)
    def index_attributemapping_test(self, mock_wsa):
        iu = Indexer(self.cfg)
        iu.ws.get_objects2.return_value = self.attribute_mapping
        res = iu.attributemapping_index(self.upa)
        self.assertIsNotNone(res)
        self.assertIn('data', res)

    @patch('Utils.Indexer.WorkspaceAdminUtils', autospec=True)
    def index_kbasematrices_test(self, mock_wsa):
        iu = Indexer(self.cfg)
        iu.ws.get_objects2.return_value = self.amplicon_matrix
        iu.attributemapping_index = Mock(return_value=self.parsed_attribute_mapping)
        res = iu.kbasematrices_index(self.upa)
        self.assertIsNotNone(res)
        self.assertIn('data', res)
