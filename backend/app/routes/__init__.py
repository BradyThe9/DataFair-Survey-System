#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes Package for DataFair Survey System
"""

from .auth import auth_bp
from .api import api_bp
from .surveys import surveys_bp

__all__ = ['auth_bp', 'api_bp', 'surveys_bp']