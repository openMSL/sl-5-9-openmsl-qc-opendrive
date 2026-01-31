# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_lanesection_min_length"
CHECKER_DESCRIPTION = "Length of lanesections shall be greater than epsilon"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_lanesection_min_length"

LANESECTION_MIN_LENGTH = 0.02

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]
        laneSections = get_sorted_lane_sections_with_length_from_road(road)
        for laneSection in laneSections:
            if laneSection.length < LANESECTION_MIN_LENGTH and laneSection.length >= 0.0:
                s_coordinate = get_s_from_lane_section(laneSection.lane_section)
                description = f"road {roadID} has too short laneSection s={s_coordinate} (lengths: {laneSection.length})"

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
                    xpath=checker_data.input_file_xml_root.getpath(laneSection.lane_section),
                    description=description,
                )
                # add 3d point
                inertial_point = get_point_xyz_from_road_reference_line(road, s_coordinate)
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
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_lanesection_min_length

    Description: Length of lanesections shall be greater than epsilon.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_lanesection_min_length check.")

    _check_all_roads(checker_data)
