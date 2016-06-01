# -*- coding: utf-8 -*-

"""
This module links fn.pyw to initiation and pileline modules.

This version works with the very simple demo code in dummystart.py and dummy[123].py
Create a new version of this for a real application.
The fn.pyw code accesses the four tuple elements defined in this module.
"""

import dummy1
import dummy2
import dummy3
import dummystart as begin

main = begin.main # this procedure is called while the splash screen is being displayed
sstime = begin.sstime # the minimum splash screen time (in seconds)

# tuples specify Pages in the Application
# 1. Text to appear in the Tab in the application
# 2. configuration filename for the pipeline
# 3. function to call when "Run" is clicked

pages = [
        ("Main", "dummyapp/cfg1.tab", dummy1.run_pipeline, None),
        ("Tab #1", "dummyapp/cfg2.tab", dummy2.run_pipeline, None),
        # ("Lobstr", "dummyapp/lobstrSE.cfg", dummy1.run_pipeline, None),    # testing using Cam's file
        # the following line has an inner Notebook with two Tabs for more complex arguments
        ("Tab #2", "dummyapp/cfg3.tab", dummy3.pipecode, [("Subtab #1", "dummyapp/cfg3.1.tab"), ("Subtab #2", "dummyapp/cfg3.2.tab")])
    ]
