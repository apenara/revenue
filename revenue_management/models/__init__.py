#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de inicialización para los modelos de datos
"""

from models.base_model import BaseModel
from models.room import Room
from models.booking import RawBooking
from models.stay import RawStay
from models.historical_summary import HistoricalSummary
from models.daily_occupancy import DailyOccupancy
from models.daily_revenue import DailyRevenue
from models.forecast import Forecast
from models.recommendation import ApprovedRecommendation
from models.rule import Rule