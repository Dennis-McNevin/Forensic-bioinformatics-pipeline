# -*- coding: utf-8 -*-

# import each of your python pipeline modules ...

import dummy
import dummystart as begin

main = begin.main
sstime = begin.sstime

# tuples specify Pages in the Application
# 1. Text to appear in the Tab in the application
# 2. configuration filename for the pipeline
# 3. function to call when "Run" is clicked

pages = [
        ("Main", "cfg.tab", dummy.run_pipeline),
        ("Tab #1", "cfg2.tab", dummy.run_pipeline)
    ]