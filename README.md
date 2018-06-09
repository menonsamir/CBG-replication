# Triangulation Using RTT

We replicated the result from Gueye et al., "Constraint-Based Geolocation of Internet Hosts",  SIGCOMM IMC 2004 using modern data. We built our replication entirely from the source material and new data; we never had access to the original data or code.

The central finding of the paper is confirmed: a series of RTT measurements to hosts with known locations can produce a relatively accurate estimate of geolocation. In our tests in the United States and Western Europe, we achieve median errors of less than 70km.


## Instructions for replication

Requirements: Python 2.7 with matplotlib, numpy, scipy, and shapely

1. (optional) Run `python geturls.py` to fetch new ping data. This takes a while and will issue many API requests. You can change the window of time you are fetching for by changing 'START_DATE' and 'STOP_DATE' at the top of the file. A long window of time will take much, much longer to fetch. At the end, you will have 'ping_mins.json' and 'figure1.png'. By default, this just uses the pre-existing 'ping_mins.json' - you can force it to do a new fetch by setting 'DO_FETCH' at the top of the file to True.
2. Run `python do_analysis.py` to run the analysis and generate all the figures. They will be saved as 'figure3a.png' and 'figure3b.png'. You can safely ignore the divide by zero warnings, they are handled by the code properly.

The "anchor_info_detail.json", "anchor_info.json", "anchor_onlyrelevant.json", and "measurement_urls.json" files contain ONLY metadata about the RIPE Atlas anchors (like their location, URLs to fetch from, etc). They should be fixed, so I have saved them in the repo itself. If you'd like to fetch new ones, the code for doing do is in 'geturls.py'.
