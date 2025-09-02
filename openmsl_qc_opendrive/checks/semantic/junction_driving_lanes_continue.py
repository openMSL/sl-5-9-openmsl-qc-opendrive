# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from lxml import etree
from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from openmsl_qc_opendrive.base import models, utils

CHECKER_ID = "check_openmsl_xodr_junction_driving_lanes_continue"
CHECKER_DESCRIPTION = "check road lane links of juction connection - each driving lane of the incoming roads must have a connection in the junction"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.junction_driving_lanes_continue"

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

def getDrivingLanesTowardsJunction(road: etree._Element, junctionID: int):
    drivingLanes = list()
    rule = utils.get_traffic_hand_rule_from_road(road)

    # check if pred and/or succ of road is junction
    predecessor = utils.get_linked_junction_id(road, models.LinkageTag.PREDECESSOR)
    successor = utils.get_linked_junction_id(road, models.LinkageTag.SUCCESSOR)
    foundLinkedRoad = False
    if predecessor is not None and predecessor == junctionID:
        foundLinkedRoad = True
        laneSection = utils.get_first_lane_section(road)
        if rule == models.TrafficHandRule.LHT:
            lanes = utils.get_right_lanes_from_lane_section(laneSection)
        else:
            lanes = utils.get_left_lanes_from_lane_section(laneSection)
        for lane in lanes:
            laneType = lane.attrib['type']
            if (laneType == "driving" or laneType == "entry" or laneType == "exit" or laneType == "onRamp" or laneType == "offRamp" or 
                laneType == "connectionRamp"):            # TODO more lanetypes? .... use config file
                drivingLanes.append(lane.attrib['id'])
    if successor is not None and successor == junctionID:
        foundLinkedRoad = True
        laneSection = utils.get_last_lane_section(road)
        if rule == models.TrafficHandRule.LHT:
            lanes = utils.get_left_lanes_from_lane_section(laneSection)
        else:
            lanes = utils.get_right_lanes_from_lane_section(laneSection)
        for lane in lanes:
            laneType = lane.attrib['type']
            if (laneType == "driving" or laneType == "entry" or laneType == "exit" or laneType == "onRamp" or laneType == "offRamp" or 
                laneType == "connectionRamp"):            # TODO more lanetypes? .... use config file
                drivingLanes.append(lane.attrib['id'])

    return drivingLanes, foundLinkedRoad  

def _check_all_junctions(checker_data: models.CheckerData) -> None:
    roads = utils.get_road_id_map(checker_data.input_file_xml_root)
    junctions = utils.get_junctions(checker_data.input_file_xml_root)

    for junction in junctions:
        junctionID = utils.to_int(junction.attrib["id"])

        # get all roads that lead into the junction and their linked lanes
        incomingRoadDict = {}
        connections = utils.get_connections_from_junction(junction)
        for connection in connections:
            incomingRoadID = utils.get_incoming_road_id_from_connection(connection)
            laneLinks = utils.get_lane_links_from_connection(connection)
            if incomingRoadID in incomingRoadDict:
                for lanelink in laneLinks:
                    incomingRoadDict[incomingRoadID].add(lanelink.attrib['from'])
            else:
                newLinkedLanes = set()
                for lanelink in laneLinks:
                    newLinkedLanes.add(lanelink.attrib['from'])
                incomingRoadDict[incomingRoadID] = newLinkedLanes

        for incomingRoadID, linkedLanes in incomingRoadDict.items():
            # find incoming road
            road = roads.get(incomingRoadID)
            if road is None:
                continue                            # checked by schema

            # get driving lanes of incoming road and check if all are linked
            drivingLanes, foundLinkedRoad = getDrivingLanesTowardsJunction(road, junctionID)
            if not foundLinkedRoad:
                continue                            # checked by schema

            if len(drivingLanes) == 0:
                registerIssue(checker_data, f"junction {junctionID} has linked road {incomingRoadID} without driving lanes towards junction", junction)
                continue

            for drivingLane in drivingLanes:
                if drivingLane not in linkedLanes:
                    registerIssue(checker_data, f"junction {junctionID} has no connection to driving lane {drivingLane} of road {incomingRoadID}", junction)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.junction_driving_lanes_continue

    Description: check road lane links of juction connection - each driving lane of the incoming roads must have a connection in the junction.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.junction_driving_lanes_continue check.")

    _check_all_junctions(checker_data)
