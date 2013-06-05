#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed import settings
from seed import deploy
import logging
logger = logging.getLogger(__name__)
logger.debug("main module invoked")
deploy.run()
