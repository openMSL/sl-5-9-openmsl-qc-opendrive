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

CHECKER_ID = "check_openmsl_xodr_road_object_size"
CHECKER_DESCRIPTION = "check if object size is valid - width and length, radius and height in range"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.object_size"

MAX_OBJECT_LENGTH = 50
MAX_OBJECT_WIDTH = 50
MAX_OBJECT_RADIUS = 50
MAX_OBJECT_HEIGHT = 50

def check_object_size(road: etree.Element, object: etree.Element, checker_data: models.CheckerData) -> None:
    roadID = road.attrib["id"]
    objectID = object.attrib["id"]
    objectS = to_float(object.attrib["s"])
    objectT = to_float(object.attrib["t"])

    # check if width + length or radius is present
    issue_descriptions = []
    objectLengthAttrib = object.attrib.get("length")
    objectWidthAttrib = object.attrib.get("width")
    objectRadiusAttrib = object.attrib.get("radius")
    if not objectLengthAttrib and not objectWidthAttrib and not objectRadiusAttrib:
        issue_descriptions.append(f"object {objectID} of road {roadID} has no defined size. Length and width or radius must be provided")
    elif objectRadiusAttrib and (objectLengthAttrib or objectWidthAttrib):
        return # checked by schema
    elif objectRadiusAttrib:
        objectRadius = to_float(object.attrib["radius"])
        if objectRadius < 0.0 or objectRadius > MAX_OBJECT_RADIUS:          # TODO 3x < 0.0 check-> should be done by schema checks already, but is not done in 1.5 (and onyl in 2 cases in 1.7)
            issue_descriptions.append(f"object {objectID} of road {roadID} has invalid radius {objectRadius} out of range (0-{MAX_OBJECT_RADIUS})")
    else:
        objectLength = to_float(object.attrib["length"])
        objectWidth = to_float(object.attrib["width"])
        if objectLength < 0.0 or objectLength > MAX_OBJECT_LENGTH:
            issue_descriptions.append(f"object {objectID} of road {roadID} has invalid length {objectLength} out of range (0-{MAX_OBJECT_LENGTH})")
        if objectWidth < 0.0 or objectWidth > MAX_OBJECT_WIDTH:
            issue_descriptions.append(f"object {objectID} of road {roadID} has invalid width {objectWidth} out of range (0-{MAX_OBJECT_WIDTH})")

    # check height
    objectHeight = to_float(object.attrib["height"])     
    if objectHeight > MAX_OBJECT_HEIGHT:
        issue_descriptions.append(f"object {objectID} of road {roadID} has too high height value {objectHeight} (max = {MAX_OBJECT_HEIGHT})")

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
            check_object_size(road, object, checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.object_size

    Description: check if object size is valid - width and length, radius and height in range.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.object_size check.")

    _check_all_roads(checker_data)
