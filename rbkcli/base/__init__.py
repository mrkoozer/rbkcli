"""Module that provides base class with portable tools/methods."""
from __future__ import print_function

import os
from logging import ERROR, WARNING

from .api import ApiRequester, RubrikApiHandler
from .essentials import CONSTANTS, DotDict, RbkcliException
from .jsops import DynaTable, RbkcliJsonOps
from .tools import RbkcliLogger, RbkcliTools

try:
    PermissionError
except NameError:
    PermissionError = IOError


class RbkcliBase:
    """Define the base class for other classes."""

    def __init__(self, log_name='empty', module='', user_profile='config',
                 base_folder='', log_mode='', workflow='command'):
        """Initialize base class."""
        self.create_base_folder(base_folder)
        if log_name == 'empty':
            log_name = CONSTANTS.LOGS_FOLDER + '/rbkcli.log'
        self.rbkcli_logger = RbkcliLogger(log_name, module, mode=log_mode)
        self.user_profile = user_profile
        self.conf_dict = DotDict({})
        self.verify_config_keys()
        self.workflow = workflow

    def json_ops(self, json_data=None):
        """Instantiate a new RbkcliJsonOps object."""
        if not json_data:
            json_data = []
        return RbkcliJsonOps(self.rbkcli_logger, json_data)

    def tools(self):
        """Instantiate a new set of RbkcliTools object."""
        return RbkcliTools(self.rbkcli_logger, conf_dict=self.conf_dict,
                           workflow=self.workflow)

    @staticmethod
    def dot_dict(dict_=None):
        """Instantiate a new dot dictionary."""
        if not dict_:
            dict_ = {}
        new_dict_ = DotDict()
        for keys, values in dict_.items():
            new_dict_[keys] = values
        return new_dict_

    def dyna_table(self, headers, rows, **kwargs):
        """Instantiate a new dynamic table dictionary."""
        return DynaTable(headers, rows, logger=self.rbkcli_logger,
                         kwargs=kwargs)

    def api_requester(self, auth):
        """Instantiate a new API requester."""
        return ApiRequester(self.rbkcli_logger, self.user_profile, auth=auth)

    def api_handler(self, auth, version):
        """Instantiate a new API handler."""
        return RubrikApiHandler(self.rbkcli_logger, auth=auth, version=version,
                                user_profile=self.user_profile)

    def verify_config_keys(self):
        """Verify configuration file and adapt parameters."""
        self.conf_dict = RbkcliTools(self.rbkcli_logger).load_conf_file()
        self.verify_loglevel()

        # Get valid user profile from configuration file, else admin profile.
        try:
            user_profile = self.conf_dict['config']['userProfile']['value']
            if self.user_profile == 'config':
                if user_profile in CONSTANTS.USERS_PROFILE:
                    self.user_profile = user_profile
                else:
                    self.user_profile = 'admin'
        except KeyError:
            self.user_profile = 'admin'

    def verify_loglevel(self):
        """Update log level in case config was changed."""
        new_log_level = self.conf_dict['config']['logLevel']['value']
        if new_log_level == 'error':
            self.rbkcli_logger.logger.setLevel(ERROR)
        elif new_log_level == 'warning':
            self.rbkcli_logger.logger.setLevel(WARNING)

    @staticmethod
    def create_base_folder(base_folder):
        """Create base folder if doesn't exists already."""
        if base_folder != '':
            CONSTANTS.BASE_FOLDER = base_folder
        try:
            if not os.path.isdir(CONSTANTS.BASE_FOLDER):
                os.mkdir(CONSTANTS.BASE_FOLDER)

        except PermissionError as error:
            print(error)
            raise RbkcliException.ToolsError(error)
            # exit()
