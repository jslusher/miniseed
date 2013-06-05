# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class SeedException(Exception):
    pass

class SeedProfileDoesNotExistError(SeedException):
    pass

class SeedProfileError(SeedException):
    pass

class SeedDriverNotSupportedError(SeedException):
    pass

class SeedImageNotAvailableError(SeedException):
    pass

class SeedZeroNameError(SeedException):
    pass

class SeedKeyPairExistsError(SeedException):
    pass

class SeedAMIDoesNotExistError(SeedException):
    pass

class SeedMachineDoesNotExistError(SeedException):
    pass

class SeedKeyPairDoesNotExistError(SeedException):
    pass

class SeedDuplicateNameError(SeedException):
    pass
class SeedDomainExistError(SeedException):
    pass
class SeedDomainDoesNotExistError(SeedException):
    pass
class SeedInvalidCredentials(SeedException):
    pass
class SeedMasterIsNotMinionError(SeedException):
    pass