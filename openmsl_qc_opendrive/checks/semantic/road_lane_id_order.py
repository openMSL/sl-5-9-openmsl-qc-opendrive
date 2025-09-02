# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity
from lxml import etree

from openmsl_qc_opendrive import constants
from openmsl_qc_opendrive.base import models, utils

CHECKER_ID = "check_openmsl_xodr_road_lane_id_order"
CHECKER_DESCRIPTION = "lane order should be continuous and without gaps"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_lane_id_order"

# check lane order of one lane section side
def check_LaneID_Order(road: etree._ElementTree, laneSection: etree._ElementTree, side: str, checker_data: models.CheckerData) -> None:
    # get lanes and starting lane id
    if side == "left": 
        lanes = utils.get_left_lanes_from_lane_section(laneSection)
        startLaneID = len(lanes)
    elif side == "right":
        lanes = utils.get_right_lanes_from_lane_section(laneSection)
        startLaneID = -1

    # check lane ids
    s_coordinate = utils.get_s_from_lane_section(laneSection)
    roadID = road.attrib["id"]       
    issue_descriptions = []
    for lane in lanes:
        laneID = int(lane.attrib["id"])
        if startLaneID != laneID:
            issue_descriptions.append(f"road {roadID} laneSection s={s_coordinate} lane {laneID} has invalid order - should be {startLaneID}")
        startLaneID -= 1

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
            xpath=checker_data.input_file_xml_root.getpath(lane),
            description=description,
        )

        if s_coordinate is None:
            continue

        # add 3d point
        inertial_point = utils.get_point_xyz_from_road_reference_line(road, s_coordinate)
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
    roads = utils.get_roads(checker_data.input_file_xml_root)

    for road in roads:
        laneSections = utils.get_lane_sections(road)
        for laneSection in laneSections:
            check_LaneID_Order(road, laneSection, "left", checker_data)
            check_LaneID_Order(road, laneSection, "right", checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_lane_id_order

    Description: lane order should be continuous and without gaps

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_lane_id_order check.")

    _check_all_roads(checker_data)
