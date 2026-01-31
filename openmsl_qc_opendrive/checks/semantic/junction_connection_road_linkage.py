# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from lxml import etree
from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_junction_connection_road_linkage"
CHECKER_DESCRIPTION = "Connection Roads need Predecessor and Successor. Connection Roads should be registered in Connection"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.junction_connection_road_linkage"

def registerIssue(checker_data: models.CheckerData, description : str, treeElement: etree._ElementTree) -> None:
    issue_id = checker_data.result.register_issue(
        checker_bundle_name=constants.BUNDLE_NAME,
        checker_id=CHECKER_ID,
        description=description,
        level=IssueSeverity.WARNING,
        rule_uid=RULE_UID,
    )

    # add xml location
    checker_data.result.add_xml_location(
        checker_bundle_name=constants.BUNDLE_NAME,
        checker_id=CHECKER_ID,
        issue_id=issue_id,
        xpath=checker_data.input_file_xml_root.getpath(treeElement),
        description=description,
    )

def _check_all_junctions(checker_data: models.CheckerData) -> None:
    roads = get_road_id_map(checker_data.input_file_xml_root)
    junctions = get_junctions(checker_data.input_file_xml_root)

    for junction in junctions:
        junctionID = junction.attrib["id"]
        connections = get_connections_from_junction(junction)

        connectionRoads = []
        for connection in connections:
            connectingRoadId = get_connecting_road_id_from_connection(connection)
            if connectingRoadId is None:                    # direct junctions have no connection roads
                continue                                        

            if connectingRoadId not in connectionRoads:
                connectionRoads.append(connectingRoadId)

            connectingRoad = roads.get(connectingRoadId)
            if connectingRoad is None:
                continue                            # checked by schema

            predecessorId = get_predecessor_road_id(connectingRoad)
            predecessor = roads.get(predecessorId)
            successorId = get_successor_road_id(connectingRoad)
            successor = roads.get(successorId)
            if predecessor is None or successor is None:
                registerIssue(checker_data, f"connectingRoad {connectingRoadId} of junction {junctionID} has no predecessor or successor!", connection)

        searchString = "./road[@junction='" + junctionID + "']"
        for road in checker_data.input_file_xml_root.findall(searchString):
            roadID = to_int(road.attrib['id'])
            if roadID not in connectionRoads:
                # check if road has driving lanes - if not it does not need a connection entry
                foundDrivingLane = False
                laneSection_list = get_lane_sections(road)
                for laneSection in laneSection_list:
                    lane_list = get_left_and_right_lanes_from_lane_section(laneSection)
                    for lane in lane_list:
                        laneType = get_type_from_lane(lane)
                        if laneType == "driving":
                            foundDrivingLane = True

                if foundDrivingLane:
                    registerIssue(checker_data, f"road {roadID} belongs to junction {junctionID}, but no connection for this road exists!", road)


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.junction_connection_road_linkage

    Description: Connection Roads need Predecessor and Successor. Connection Roads should be registered in Connection.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.junction_connection_road_linkage check.")

    _check_all_junctions(checker_data)
