# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 20:34:40 2021

@author: SYue
"""

import os
import math
import datetime
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.special import binom
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import ColorbarBase