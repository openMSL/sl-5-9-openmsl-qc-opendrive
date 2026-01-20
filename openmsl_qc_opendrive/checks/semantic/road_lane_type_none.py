# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_lane_type_none"
CHECKER_DESCRIPTION = "Lane Type shall not be None"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.lane_type.none"

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]

        laneSection_list = get_lane_sections(road)
        for laneSection in laneSection_list:
            s_coordinate = get_s_from_lane_section(laneSection)

            lane_list = get_left_and_right_lanes_from_lane_section(laneSection)
            for lane in lane_list:
                laneType = get_type_from_lane(lane)
                if laneType != "none":
                    continue               

                # register issue
                laneID = lane.attrib["id"]
                description = f"road {roadID} has invalid lanetype {laneType} in laneSection s={s_coordinate} lane={str(laneID)}"                    
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
                inertial_point = get_middle_point_xyz_at_height_zero_from_lane_by_s(road, laneSection, lane, s_coordinate)
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


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.lane_type.none

    Description: Lane Type shall not be None.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.lane_type.none check.")

    _check_all_roads(checker_data)
