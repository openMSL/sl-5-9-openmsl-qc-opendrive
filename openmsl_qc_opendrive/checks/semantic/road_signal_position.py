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

CHECKER_ID = "check_openmsl_xodr_road_signal_position"
CHECKER_DESCRIPTION = "check if signal position is valid - s value is in range of road length, t and zOffset in range"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.signal_position"

EPSILON_S_ON_ROAD = 0.000001
MAX_RANGE_SIGNAL_T = 50
MAX_RANGE_SIGNAL_ZOFFSET = 20

# check signal postion 
def check_signal_postion_for_road(road: etree.Element, signal: etree.Element, checker_data: models.CheckerData):
    roadID = road.attrib["id"]
    signalID = signal.attrib["id"]
    signalS = to_float(signal.attrib["s"])   
    signalT = to_float(signal.attrib["t"])     

    # check s position
    issue_descriptions = []
    roadLength = get_road_length(road)
    if signalS - roadLength > EPSILON_S_ON_ROAD:
        issue_descriptions.append(f"signal {signalID} of road {roadID} has too high s value {signalS} (road length = {roadLength})")
        signalS = roadLength        

    # check t position
    if signalT < -MAX_RANGE_SIGNAL_T or signalT > MAX_RANGE_SIGNAL_T:
        issue_descriptions.append(f"signal {signalID} of road {roadID} has t value {signalT} out of range (-{MAX_RANGE_SIGNAL_T}, +{MAX_RANGE_SIGNAL_T})")

    # check z position
    if signal.tag != "signalReference":
        signalZOffset = to_float(signal.attrib["zOffset"])
        if signalZOffset < -MAX_RANGE_SIGNAL_ZOFFSET or signalZOffset > MAX_RANGE_SIGNAL_ZOFFSET:
            issue_descriptions.append(f"signal {signalID} of road {roadID} has zOffset value {signalZOffset} out of range (-{MAX_RANGE_SIGNAL_ZOFFSET}, +{MAX_RANGE_SIGNAL_ZOFFSET})")

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
            xpath=checker_data.input_file_xml_root.getpath(signal),
            description=description,
        )

        # add 3d point
        inertial_point = get_point_xyz_from_road(road, signalS, signalT, 0.0)
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
        for signal in road.findall("./signals/signal"):
            check_signal_postion_for_road(road, signal, checker_data)         
        for signal in road.findall("./signals/signalReference"):
            check_signal_postion_for_road(road, signal, checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.signal_position

    Description: check if signal position is valid - s value is in range of road length, t and zOffset in range.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.signal_position check.")

    _check_all_roads(checker_data)
