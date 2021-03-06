''' Snap4city GTFS processor.
   Copyright (C) 2021 DISIT Lab http://www.disit.org - University of Florence
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Affero General Public License for more details.
   You should have received a copy of the GNU Affero General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
# author: DISIT - S4C - https://github.com/disit/snap4city/blob/master/Snap4CityGTFS/chouette-gtfs-n3.py
# modified by: Giorgos Zoutis aka Necrokefalos
# version: v0.1

from zipfile import ZipFile
import pandas as pd
import os, pytz, datetime, argparse

import json, sys

 
class Converter:

    _route_type = {
        0: "<http://vocab.gtfs.org/terms#LightRail>",
        1: "<http://vocab.gtfs.org/terms#Subway>",
        2: "<http://vocab.gtfs.org/terms#Rail>",
        3: "<http://vocab.gtfs.org/terms#Bus>",
        4: "<http://vocab.gtfs.org/terms#Ferry>",
        5: "<http://vocab.gtfs.org/terms#CableCar>",
        6: "<http://vocab.gtfs.org/terms#Gondola>",
        7: "<http://vocab.gtfs.org/terms#Funicular>"
    }

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.getcwd() + os.sep + 'output'
        else:
            output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        self.output_directory = output_dir
    
    def __str__(self):
        return """Output directory: %s""" \
               % (self.output_directory)

    def set_output_directory(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.getcwd() + os.sep + 'output'
        else:
            output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        self.output_directory = output_dir

    def _extract_agencies_triples(self, entry_name):
        agency = pd.read_csv(self.output_directory + os.sep + 'agency.txt', delimiter=',')
        print("Write triples for agency")
        f = open(self.output_directory + os.sep + "agency.n3", "w+")
        for i in range(len(agency["agency_id"])):
            # semantic subject
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Agency_" + str(agency["agency_id"][i]) + \
                         ">"

            f.write(first_term + " <http://purl.org/dc/terms/identifier> " +
                    '"' + entry_name + '_' + str(agency["agency_id"][i]) + '" .\n')
            f.write(first_term + " <http://xmlns.com/foaf/0.1/name> " + '"' + str(agency["agency_name"][i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#timeZone> " + '"' + str(agency["agency_timezone"][i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#fareUrl> " + '"' + str(agency["agency_url"][i]) + '" .\n')
            f.write(
                first_term + " <http://purl.org/dc/terms/language> " + '"' + str(agency["agency_lang"][i]) + '" .\n')
            f.write(
                first_term +
                " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Agency> . \n")
            f.write("\n")
        f.close()

    def _extract_calendar_dates_triples(self, entry_name):
        read_file = pd.read_csv(self.output_directory + os.sep + 'calendar_dates.txt')
        read_file.to_csv(r'calendar_dates.csv', index=None)
        calendar = pd.read_csv("calendar_dates.csv", delimiter=",")
        print("Write triples for calendar_dates")
        f = open(self.output_directory + os.sep + "calendar_dates.n3", "w+")
        for i in range(len(calendar["service_id"])):
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Service_" + str(calendar["service_id"][i]) + ">"
            date = str(calendar["date"][i])[0:4] + "-" + str(calendar["date"][i])[4:6] + "-" + str(calendar["date"][i])[6:8]

            f.write(first_term + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Service_" +
                    str(calendar["service_id"][i]) + '" .\n')
            f.write(
                first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Service> .\n")
            f.write(first_term + " <http://purl.org/dc/terms/date>" + '"' + date + '" .\n')
            f.write("\n")
        f.close()

    def _extract_stop_triples(self, entry_name):
        read_file = pd.read_csv(self.output_directory + os.sep + 'stops.txt')
        read_file.to_csv(r'stops.csv', index=None)
        stops = pd.read_csv("stops.csv", delimiter=",")
        print("Write triples for stops")
        f = open(self.output_directory + os.sep + 'stops.n3', "w+")
        for i in range(len(stops["stop_id"])):
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Stop_" + str(stops["stop_id"][i]) + ">"

            f.write(first_term + " <http://www.w3.org/2003/01/geo/wgs84_pos#long> " + '"' + str(
                stops["stop_lon"][i]) + '"^^<http://www.w3.org/2001/XMLSchema#float> .\n')
            f.write(
                first_term + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Stop_" + str(stops["stop_id"][
                    i]) + '" .\n')
            f.write(first_term + " <http://vocab.gtfs.org/terms#code> " + '"' + str(stops["stop_code"][i]) + '" .\n')
            f.write(first_term + " <http://www.w3.org/2003/01/geo/wgs84_pos#lat> " + '"' + str(
                stops["stop_lat"][i]) + '"^^<http://www.w3.org/2001/XMLSchema#float> .\n')
            f.write(
                first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Stop> .\n")
            f.write(first_term + " <http://xmlns.com/foaf/0.1/name> " + '"' +
                    str(stops["stop_name"][i]).replace('"', r'\"') + '" .\n')
            f.write(
                first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.disit.org/km4city/schema#BusStop> .\n")
            f.write("\n")
        f.close()

    def _extract_stop_times_triples(self, entry_name):
        read_file = pd.read_csv(self.output_directory + os.sep + 'stop_times.txt')
        read_file.to_csv(r'stop_times.csv', index=None)
        stop_times = pd.read_csv("stop_times.csv", delimiter=",")
        print("Write triples for stop_times")
        f = open(self.output_directory + os.sep + 'StopTimes.n3', "w+")
        for i in range(len(stop_times["trip_id"])):
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_StopTime_" + str(stop_times["trip_id"][
                i]) + "_" + str(stop_times["stop_sequence"][i]) + "> "
            first_term_var = "<http://www.disit.org/km4city/resource/" + entry_name + "_Trip_" + str(stop_times["trip_id"][
                i]) + "> "
            first_term_var2 = "<http://www.disit.org/km4city/resource/" + entry_name + "_Stop_" + str(stop_times["stop_id"][
                i]) + ">"

            f.write(first_term + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_StopTime_" +
                    str(stop_times["trip_id"][i]) + "_" + str(stop_times["stop_sequence"][i]) + '" .\n')
            f.write(
                first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#StopTime> .\n")
            f.write(
                first_term_var + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Trip> .\n")
            f.write(first_term + " <http://vocab.gtfs.org/terms#trip> " + first_term_var + " .\n")
            f.write(first_term + " <http://vocab.gtfs.org/terms#departureTime> " + '"' + str(stop_times["departure_time"][
                i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#stop> <http://www.disit.org/km4city/resource/" + entry_name + "_Stop_" +
                str(stop_times["stop_id"][i]) + "> .\n")
            f.write(first_term + " <http://vocab.gtfs.org/terms#stopSequence> " + '"' + str(
                stop_times["stop_sequence"][i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#arrivalTime> " + '"' + str(stop_times["arrival_time"][
                    i]) + '" .\n')
            f.write(first_term_var + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Trip_" +
                    str(stop_times["trip_id"][i]) + '" .\n')
            f.write(
                first_term_var2 + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Stop> .\n")
            f.write(first_term_var2 + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Stop_" +
                    str(stop_times["stop_id"][i]) + '" .\n')
            f.write("\n")
        f.close()

    def _extract_trips_triples(self, entry_name):
        trips = pd.read_csv(self.output_directory + os.sep + "trips.txt", delimiter=",", low_memory=True)
        print("Write triples for trips")
        f = open(self.output_directory + os.sep + "trips.n3", "w+")
        for i in range(len(trips["route_id"])):
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Trip_" + str(trips["trip_id"][i]) + ">"
            first_term_var = "<http://www.disit.org/km4city/resource/" + entry_name + "_Service_" + \
                             str(trips["service_id"][
                                 i]) + ">"
            first_term_var2 = "<http://www.disit.org/km4city/resource/" + entry_name + "_Shape_" + str(
                trips["shape_id"][i]) + ">"
            first_term_var3 = "<http://www.disit.org/km4city/resource/" + entry_name + "_Route_" + str(
                trips["route_id"][i]) + ">"
            short_name = str(trips["trip_short_name"][i])
            if short_name == "nan":
                short_name = "NULL"

            f.write(
                first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Trip> .\n")
            f.write(first_term_var + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Service_" +
                    str(trips["service_id"][i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#route> <http://www.disit.org/km4city/resource/" + entry_name + "_Route_" + str(
                    trips["route_id"][i]) + "> .\n")
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#direction> " + '"' + str(
                    trips["direction_id"][i]) + '" .\n')
            f.write(first_term_var2 + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + "_Shape_" + str(
                trips["shape_id"][i]) + '" .\n')
            f.write(
                first_term + " <http://www.opengis.net/ont/geosparql#hasGeometry> <http://www.disit.org/km4city/resource/" + entry_name + "_Shape_" + str(
                    trips["shape_id"][i]) + "> .\n")
            f.write(
                first_term_var + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Service> .\n")
            f.write(first_term + ' <http://vocab.gtfs.org/terms#shortName> "' + short_name + '" .\n')
            f.write(
                first_term_var3 + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Route> .\n")
            f.write(first_term + ' <http://purl.org/dc/terms/identifier> "' + entry_name + "_Trip_" + str(trips["trip_id"][
                i]) + '" .\n')
            f.write(
                first_term + " <http://vocab.gtfs.org/terms#service> <http://www.disit.org/km4city/resource/" + entry_name + "_Service_" +
                str(trips["service_id"][i]) + "> .\n")
            f.write(first_term_var3 + ' <http://purl.org/dc/terms/identifier> "' + entry_name + "_Route_" + str(
                trips["route_id"][i]) + '". \n')
            f.write(
                first_term_var2 + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#Geometry> .\n\n")

            f.write("\n")
        f.close()

    def _extract_shapes_triples(self, entry_name):
        shapes = pd.read_csv(self.output_directory + os.sep + 'shapes.txt', delimiter=',', low_memory=True, dtype=str)
        print("Write triples for shapes")
        shape = dict()
        for i in range(len(shapes['shape_id'])):
            if shapes['shape_id'][i] not in shape.keys():
                shape.update({shapes['shape_id'][i]: ""})
            shape[shapes['shape_id'][i]] += """, %s %s""" % (shapes['shape_pt_lon'][i], shapes['shape_pt_lat'][i])

        f = open(self.output_directory + os.sep + 'shapes.n3', 'w+')
        for element in shape.keys():
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Shape_" + str(element) + ">"
            # identifier
            f.write(first_term + " <http://purl.org/dc/terms/identifier> " + '"' + entry_name + '_Shape_' + str(
                element) + '" .\n')
            # syntax_type
            f.write(first_term + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " +
                    "<http://www.opengis.net/ont/geosparql#Geometry> .\n")
            # shape points
            f.write(first_term + ' <http://www.opengis.net/ont/geosparql#asWKT> "LINESTRING((' +
                    shape[element][2:] + '))" .\n\n')
        f.close()

    def _extract_routes_triples(self, entry_name):
        # added _agency_id since there is not a column called ageny_id in routes.csv file and there is only one agency in my case
        _agency_id = 'OASA'
        routes = pd.read_csv(self.output_directory + os.sep + "routes.txt", delimiter=",", low_memory=True)
        print("Write triples for routes")
        f = open(self.output_directory + os.sep + "routes.n3", "w+")
        for i in range(len(routes['route_id'])):
            first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Route_" + str(
                routes["route_id"][i]) + ">"
            # replaced this since there is no agency_id in route files and there is onle one agency available
            #agency_first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Agency_" + \
            #                    str(routes["agency_id"][i]) + ">"
            agency_first_term = "<http://www.disit.org/km4city/resource/" + entry_name + "_Agency_" + \
                                _agency_id + ">"
            f.write(first_term + """ <http://purl.org/dc/terms/identifier> "%s_Route_%s" . \n"""
                    % (entry_name, str(routes['route_id'][i])))
            f.write("""%s <http://vocab.gtfs.org/terms#color> "%s" .\n""" % (first_term, routes['route_color'][i]))
            f.write(
                """%s <http://vocab.gtfs.org/terms#textColor> "%s" .\n""" % (first_term, routes['route_text_color'][i]))
            f.write("""%s <http://vocab.gtfs.org/terms#longName> "%s" .\n""" % (
            first_term, str(routes['route_long_name'][i]).replace('"', r'\"')))
            f.write("""%s <http://vocab.gtfs.org/terms#shortName> "%s" . \n""" % (first_term,
                                                                                  str(routes['route_short_name'][
                                                                                          i]).replace('"', r'\"')))
            #f.write("""%s <http://purl.org/dc/terms/identifier> "%s_Agency_%s" . \n""" % (agency_first_term, entry_name,
            #                                                                              str(routes['agency_id'][i])))
            f.write("""%s <http://purl.org/dc/terms/identifier> "%s_Agency_%s" . \n""" % (agency_first_term, entry_name,
                                                                                          _agency_id))
            f.write("""%s <http://vocab.gtfs.org/terms#agency> %s .\n""" % (first_term, agency_first_term))
            f.write("""%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Agency> .\n"""
                    % agency_first_term)
            f.write("""%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#Route> .\n"""
                    % first_term)
            if (id := int(routes['route_type'][i])) in range(0, 8):
                # id definiti tra 0 e 7, vedi _route_type
                f.write(
                    """%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vocab.gtfs.org/terms#RouteType> . \n"""
                    % self._route_type[id])
                f.write("""%s <http://vocab.gtfs.org/terms#routeType> %s . \n\n""" % (first_term, self._route_type[id]))

    def _extract_triple(self, entry_name, file_path, save_original: bool = False):
        # per testare un file di prova decommentare sotto
        # file_path = os.path.abspath('Bus_cttnordlucca-2.gtfs')
        print(file_path)
        with ZipFile(file_path, 'r') as zip_obj:
            zip_obj.extractall(self.output_directory)
        self._extract_agencies_triples(entry_name)
        self._extract_calendar_dates_triples(entry_name)
        self._extract_stop_triples(entry_name)
        self._extract_stop_times_triples(entry_name)
        self._extract_trips_triples(entry_name)
        self._extract_shapes_triples(entry_name)
        self._extract_routes_triples(entry_name)

        data_version = """<http://www.disit.org/km4city/resource/%s> <http://purl.org/dc/terms/date> "%s"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
        """ % (entry_name, datetime.datetime.now(pytz.utc).isoformat())
        f = open(self.output_directory + os.sep + "dataset_version.n3", 'w+')
        f.write(data_version)
        f.close()

        if os.path.exists(self.output_directory + os.sep + "agency.txt"):
            os.remove(self.output_directory + os.sep + "agency.txt")
        
        if os.path.exists(self.output_directory + os.sep + "calendar_dates.txt"):
            os.remove(self.output_directory + os.sep + "calendar_dates.txt")

        if os.path.exists(self.output_directory + os.sep + "calendar.txt"):
            os.remove(self.output_directory + os.sep + "calendar.txt")

        if os.path.exists(self.output_directory + os.sep + "routes.txt"):
            os.remove(self.output_directory + os.sep + "routes.txt")

        if os.path.exists(self.output_directory + os.sep + "shapes.txt"):
            os.remove(self.output_directory + os.sep + "shapes.txt")

        if os.path.exists(self.output_directory + os.sep + "stop_times.txt"):
            os.remove(self.output_directory + os.sep + "stop_times.txt")

        if os.path.exists(self.output_directory + os.sep + "stops.txt"):
            os.remove(self.output_directory + os.sep + "stops.txt")

        if os.path.exists(self.output_directory + os.sep + "transfers.txt"):
            os.remove(self.output_directory + os.sep + "transfers.txt")

        if os.path.exists(self.output_directory + os.sep + "trips.txt"):
            os.remove(self.output_directory + os.sep + "trips.txt")

        if not save_original:
            os.remove(file_path)
    
    def get_triples(self, entry_name: str = None, save_original: bool = False):
        if entry_name is None:
            entry_name = 'Bus_OASA'

        # replace string for file_path 'public.zip' according to your file
        file_path = self.output_directory + os.sep + 'public.zip'

        return self._extract_triple(entry_name, file_path, save_original)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interface for connect to a Enroute Chouette application and export'
                                                 'publications in triples format')
    parser.add_argument('-o', '--output-directory', type=str, default=None,
                        help='The output directory of the triples. Default is inside current directory: '
                             + os.path.curdir + os.sep + 'output')
    parser.add_argument('-s', '--save', action='store_true',
                        help='This flag can be used to preserve the original GTFS export inside OUTPUT_FOLDER')
    parser.add_argument('-e', '--entry-name', type=str, default=None,
                        help='The name for the extracted data entries. Dafault Bus_OASA')
    
    args = parser.parse_args()
    #print(args)

    converter = Converter(args.output_directory)
    print('Args: [', converter, ']')
    converter.get_triples(args.entry_name, args.save)
