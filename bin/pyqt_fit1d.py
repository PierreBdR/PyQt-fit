#!/usr/bin/env python
import matplotlib
matplotlib.use('Qt5Agg')
from pyqt_fit import pyqt_fit1d
from qtpy import QtWidgets
import matplotlib

import sys
app = QtWidgets.QApplication(sys.argv)
matplotlib.interactive(True)
wnd = pyqt_fit1d.main()
sys.exit(app.exec_())

