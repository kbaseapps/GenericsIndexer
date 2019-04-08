# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from Utils.Indexer import Indexer

#END_HEADER


class GenericsIndexer:
    '''
    Module Name:
    GenericsIndexer

    Module Description:
    A KBase module: GenericsIndexer
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.indexer = Indexer(config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def attributemapping_index(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN attributemapping_index
        output = self.indexer.attributemapping_index(params['upa'])
        #END attributemapping_index

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method attributemapping_index return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def kbasematrices_index(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "Results" -> structure: parameter
           "file_name" of String, parameter "index" of unspecified object
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN kbasematrices_index
        output = self.indexer.kbasematrices_index(params['upa'])
        #END kbasematrices_index

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method kbasematrices_index return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
