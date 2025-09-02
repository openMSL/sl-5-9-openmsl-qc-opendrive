# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from enum import Enum
from lxml import etree
from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from openmsl_qc_opendrive.base import models, utils

CHECKER_ID = "check_openmsl_xodr_road_type_vs_speed_limit"
CHECKER_DESCRIPTION = "Speed Limit of Lanes should match with road type"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.road_type_vs_speed_limit"

def getSpeedRange(roadType: str) -> None:
    if roadType == "rural":
        return (50, 100)
    elif roadType == "motorway":
        return (80, 999)
    elif roadType == "town":
        return (10, 100)
    elif roadType == "lowSpeed":
        return (10, 30)
    elif roadType == "pedestrian": 
        return (1, 20)
    elif roadType == "bicycle":
        return (1, 40)
    elif roadType == "townExpressway": 
        return (80, 130)
    elif roadType == "townCollector":
        return (50, 100)
    elif roadType == "townArterial":
        return (50, 90)
    elif roadType == "townPrivate":
        return (10, 30)
    elif roadType == "townLocal":
        return (10, 30)
    elif roadType == "townPlayStreet":
        return (10, 30)
    return None

def get_speed_value(speed: etree._ElementTree) -> float:
    speedUnit = 'm/s'
    if 'unit' in speed.attrib:
        speedUnit = speed.attrib['unit']
    speedvalue = float(speed.attrib['max'])
    if speedUnit == 'm/s':
        speedvalue = speedvalue * 3.6
    elif speedUnit == 'mph':
        speedvalue = speedvalue * 1.609
    elif speedUnit == 'km/h':
        speedvalue = speedvalue
    return speedvalue

def registerIssue(checker_data: models.CheckerData, description : str, treeElement: etree._ElementTree, point: models.Point3D) -> None:
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

    if point is None:
        return

    # add 3d point
    checker_data.result.add_inertial_location(
        checker_bundle_name=constants.BUNDLE_NAME,
        checker_id=CHECKER_ID,
        issue_id=issue_id,
        x=point.x,
        y=point.y,
        z=point.z,
        description=description,
    )

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = utils.get_roads(checker_data.input_file_xml_root)

    for road in roads:
        if road.find("type") is None:
            continue                        # nothing to check, if no roadtype is given

        roadID = road.attrib["id"]
        roadType = road.find("type").attrib["type"]
        speedRange = getSpeedRange(roadType)
        if speedRange is None:
            registerIssue(checker_data, f"road {roadID} has invalid road type {roadType} or it is missing in config file", road, None)
        else:
            laneSections = utils.get_lane_sections(road)
            for laneSection in laneSections:
                s_coordinate = utils.get_s_from_lane_section(laneSection)
                lanes = utils.get_left_and_right_lanes_from_lane_section(laneSection)
                for lane in lanes:
                    laneID = lane.attrib["id"]
                    laneType = lane.attrib['type']
                    if laneType != 'driving':                                           # TODO accept more lanetypes
                        continue                        # only check driving lanes

                    for speed in lane.findall("./speed"):
                        speedvalue = get_speed_value(speed)            
                        if speedRange[0] > speedvalue or speedRange[1] < speedvalue:
                            inertial_point = utils.get_middle_point_xyz_at_height_zero_from_lane_by_s(road, laneSection, lane, s_coordinate)
                            registerIssue(checker_data, 
                                        f"road {roadID} laneSection {s_coordinate} lane {laneID} has speed value {speedvalue}km/h that is outside the valid range ({speedRange[0]} - {speedRange[1]})",
                                        lane, inertial_point)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.road_type_vs_speed_limit

    Description: Speed Limit of Lanes should match with road type.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.road_type_vs_speed_limit check.")

    _check_all_roads(checker_data)
