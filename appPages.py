# -*- coding: utf-8 -*-

"""
This module links fn.pyw to initiation and pileline modules.

This version works with the very simple demo code in dummystart.py and dummy.py
Create a new version of this for real applications.
The fn.pyw code accesses the three variables defined in this module.
"""

import dummy
import dummystart as begin

main = begin.main # this procedure is called while the splash screen is being displayed
sstime = begin.sstime # the minimum splash screen time (in seconds)

# tuples specify Pages in the Application
# 1. Text to appear in the Tab in the application
# 2. configuration filename for the pipeline
# 3. function to call when "Run" is clicked

pages = [
        ("Main", "cfg.tab", dummy.run_pipeline),
        ("Tab #1", "cfg2.tab", dummy.run_pipeline)
    ]