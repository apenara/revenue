#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Páginas de la interfaz de usuario
"""

from ui.pages.dashboard import show as dashboard_show
from ui.pages.data_ingestion import show as data_ingestion_show
from ui.pages.forecasting import show as forecasting_show
from ui.pages.pricing import show as pricing_show
from ui.pages.tariff_management import show as tariff_management_show
from ui.pages.settings import show as settings_show

# Exportar funciones show para cada página
dashboard = dashboard_show
data_ingestion = data_ingestion_show
forecasting = forecasting_show
pricing = pricing_show
tariff_management = tariff_management_show
settings = settings_show