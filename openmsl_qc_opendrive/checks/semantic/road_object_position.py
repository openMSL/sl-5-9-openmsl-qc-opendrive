# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from lxml import etree
from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_object_position"
CHECKER_DESCRIPTION = "check if object position is valid - s value is in range of road length, t and zOffset in range"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.object_position"

EPSILON_S_ON_ROAD = 0.000001
MAX_RANGE_OBJECT_T = 50
MAX_RANGE_OBJECT_ZOFFSET = 20

def check_object_postion_for_road(road: etree.Element, object: etree.Element, checker_data: models.CheckerData) -> None:
    roadID = road.attrib["id"]
    roadLength = get_road_length(road)
    objectID = object.attrib["id"]
    issue_descriptions = []

    # check s position
    objectS = to_float(object.attrib["s"])
    if objectS - roadLength > EPSILON_S_ON_ROAD:
        issue_descriptions.append(f"object {objectID} of road {roadID} has too high s value {objectS} (road length = {roadLength})")
        objectS = roadLength

    # check t position
    objectT = 0.0
    if object.tag != "tunnel" and object.tag != "bridge":
        objectT = to_float(object.attrib["t"]) 
        if objectT < -MAX_RANGE_OBJECT_T or objectT > MAX_RANGE_OBJECT_T:
            issue_descriptions.append(f"object {objectID} of road {roadID} has t value {objectT} out of range (-{MAX_RANGE_OBJECT_T}, +{MAX_RANGE_OBJECT_T})")

    # check zOffset
    if object.tag == "object":
        objectZOffset = to_float(object.attrib["zOffset"])
        if objectZOffset < -MAX_RANGE_OBJECT_ZOFFSET or objectZOffset > MAX_RANGE_OBJECT_ZOFFSET:
            issue_descriptions.append(f"object {objectID} of road {roadID} has zOffset value {objectZOffset} out of range (-{MAX_RANGE_OBJECT_ZOFFSET}, +{MAX_RANGE_OBJECT_ZOFFSET})")

    # check length of tunnel, bridge
    if object.tag == "tunnel" or object.tag == "bridge":
        objectLength = to_float(object.attrib["length"]) 
        if objectS  + objectLength - roadLength  > EPSILON_S_ON_ROAD:
            issue_descriptions.append(f"{object.tag} {objectID} of road {roadID} is too long (EndS = {objectS  + objectLength}, road length = {roadLength})")
    
    for description in issue_descriptions:
        # register issues
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
            xpath=checker_data.input_file_xml_root.getpath(object),
            description=description,
        )

        # add 3d point
        inertial_point = get_point_xyz_from_road(road, objectS, objectT, 0.0)
        if inertial_point is not None:
            checker_data.result.add_inertial_location(
                checker_bundle_name=constants.BUNDLE_NAME,
                checker_id=CHECKER_ID,
                issue_id=issue_id,
                x=inertial_point.x,
                y=inertial_point.y,
                z=inertial_point.z,
                description=description,
            )        

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        for object in road.findall("./objects/object"):
            check_object_postion_for_road(road, object, checker_data)         
        for object in road.findall("./objects/objectReference"):
            check_object_postion_for_road(road, object, checker_data)
        for object in road.findall("./objects/tunnel"):
            check_object_postion_for_road(road, object, checker_data)            
        for object in road.findall("./objects/bridge"):
            check_object_postion_for_road(road, object, checker_data)   

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.object_position

    Description: check if object position is valid - s value is in range of road length, t and zOffset in range.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.object_position check.")

    _check_all_roads(checker_data)
