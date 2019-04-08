# -*- coding: utf-8 -*-
import json
import os
import unittest
from configparser import ConfigParser
from unittest.mock import Mock

from GenericsIndexer.GenericsIndexerImpl import GenericsIndexer
from GenericsIndexer.GenericsIndexerServer import MethodContext
from installed_clients.WorkspaceClient import Workspace
from installed_clients.authclient import KBaseAuth as _KBaseAuth


class GenericsIndexerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('GenericsIndexer'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'GenericsIndexer',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.impl = GenericsIndexer(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.mock_dir = os.path.join(cls.test_dir, 'data')
        cls.schema_dir = cls.cfg['schema-dir']

        cls.amplicon_matrix = cls.read_mock('AmpliconMatrix.json')
        cls.attribute_mapping = cls.read_mock('AttributeMapping.json')
        cls.parsed_attribute_mapping = cls.read_mock('ParsedAttributeMapping.json')

        cls.params = {'upa': '1/2/3'}
        cls.impl.indexer.ws.get_objects2 = Mock()

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

    def _validate(self, sfile, data):
        schema = json.load(open(os.path.join(self.schema_dir, sfile)))
        for key in schema['schema'].keys():
            self.assertIn(key, data)

    def index_attributemapping_test(self):
        self.impl.indexer.ws.get_objects2.return_value = self.attribute_mapping
        ret = self.impl.attributemapping_index(self.ctx, self.params)[0]
        self.assertIsNotNone(ret)
        self.assertIn('data', ret)
        self.assertIn('schema', ret)
        self._validate('attributemapping_schema.json', ret['data'])
        json.dump(ret['data'], open(self.scratch+'/ParsedAttributeMapping.json', 'w'))

    def index_kbasematrices_test(self):
        self.impl.indexer.ws.get_objects2.return_value = self.amplicon_matrix
        self.impl.indexer.attributemapping_index = Mock(return_value=self.parsed_attribute_mapping)
        ret = self.impl.kbasematrices_index(self.ctx, self.params)
        self.assertIsNotNone(ret[0])
        self.assertIn('data', ret[0])
        self.assertIn('schema', ret[0])
        self._validate('kbasematrices_schema.json', ret[0]['data'])
