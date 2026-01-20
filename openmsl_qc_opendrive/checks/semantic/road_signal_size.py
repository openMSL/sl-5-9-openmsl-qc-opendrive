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

CHECKER_ID = "check_openmsl_xodr_road_signal_size"
CHECKER_DESCRIPTION = "check if signal size is valid - width and height in range"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.signal_size"

MAX_SIGNAL_WIDTH = 5
MAX_SIGNAL_HEIGHT = 5

# check signal postion 
def check_signal_size(road: etree.Element, signal: etree.Element, checker_data: models.CheckerData):
    roadID = road.attrib["id"]
    signalID = signal.attrib["id"]
    signalS = to_float(signal.attrib["s"])   
    signalT = to_float(signal.attrib["t"])   

    # check width
    issue_descriptions = []    
    signalWidth = to_float(signal.attrib["width"])
    if signalWidth > MAX_SIGNAL_WIDTH:
        issue_descriptions.append(f"signal {signalID} of road {roadID} has too high width value {signalWidth} (max = {MAX_SIGNAL_WIDTH})")

    # check height
    signalheight = to_float(signal.attrib["height"])     
    if signalheight > MAX_SIGNAL_HEIGHT:
        issue_descriptions.append(f"signal {signalID} of road {roadID} has too high height value {signalheight} (max = {MAX_SIGNAL_HEIGHT})")

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
            check_signal_size(road, signal, checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.signal_size

    Description: check if signal size is valid - width and height in range.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.signal_size check.")

    _check_all_roads(checker_data)
