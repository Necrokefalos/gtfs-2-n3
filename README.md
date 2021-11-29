# 🚏 gtfs-2-n3

## Modified solution in order to convert GTFS files to .n3 to be used in S4C.
Original script: https://github.com/disit/snap4city/blob/master/Snap4CityGTFS/chouette-gtfs-n3.py

### Requirements: ###
* python 3.10
* pip3.10
  - install necessary modules with `$ pip3.10 install <module>`
- - - -

#### Data source: http://archive.data.gov.gr/dataset/oasa-gtfs

### Quick Guide

#### Create directory named `/output` inside repo, download file outside of repo and copy it to `/output` directory:

`
$ wget http://archive.data.gov.gr/dataset/76aae6a7-dd11-4586-bee8-94b599a4752b/resource/804e5a69-d5c8-4379-a67b-214a69226311/download/public.zip
`

#### Script usage example:
`
$ python3.10 gtfs2n3.py
`
