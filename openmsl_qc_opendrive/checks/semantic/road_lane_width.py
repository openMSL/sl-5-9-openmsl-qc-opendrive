# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity
from scipy.optimize import minimize_scalar

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_lane_width"
CHECKER_DESCRIPTION = "Lane width must always be greater than zero or at the start/end point of a lanesection greater or equal to zero"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_lane_width"

EPSILON_ZERO_WIDTH = -0.01

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]
        laneSections = get_sorted_lane_sections_with_length_from_road(road)
        for laneSection in laneSections:
            lanes = get_left_and_right_lanes_from_lane_section(laneSection.lane_section)
            sOfSection = get_s_from_lane_section(laneSection.lane_section)
            for lane in lanes:
                laneID = lane.attrib["id"]
                widthPolynoms = get_lane_width_poly3_list(lane)
                for widthPoly in widthPolynoms:
                    issue_descriptions = []
                    s_coordinate = sOfSection + widthPoly.s_offset
                    if widthPoly.poly3.a < 0.0:
                        issue_descriptions.append(f"road {roadID} has invalid width:{widthPoly.poly3.a} in laneSection s={sOfSection} lane={laneID} sOffset={widthPoly.s_offset}")
                    elif widthPoly.poly3.b != 0.0 or widthPoly.poly3.c != 0.0 or widthPoly.poly3.d != 0.0:      # constant polynom does not need to be checked                  
                        # get range of polynom
                        sOffsetNext = laneSection.length
                        if widthPolynoms.index(widthPoly) < len(widthPolynoms) - 1:
                            nextElement = widthPolynoms[widthPolynoms.index(widthPoly)+1]
                            sOffsetNext = nextElement.s_offset
                        if sOffsetNext <= widthPoly.s_offset:
                            continue;                               # invalid sOffsets are checked in separate check

                        # calc minimum polynom value in range
                        def f(x):
                            return widthPoly.poly3.d * x ** 3 + widthPoly.poly3.c * x ** 2 + widthPoly.poly3.b * x + widthPoly.poly3.a                    
                        res = minimize_scalar(f, bounds=(0.0, sOffsetNext - widthPoly.s_offset), method='bounded')

                        if res.success != True:
                            issue_descriptions.append(f"road {roadID} has invalid width in laneSection s={sOfSection} lane={laneID} sOffset={widthPoly.s_offset}")
                        elif res.fun < EPSILON_ZERO_WIDTH:
                            issue_descriptions.append(f"road {roadID} has invalid width:{res.fun} in laneSection s={sOfSection} lane={laneID} sOffset={widthPoly.s_offset}")
                            s_coordinate += res.x
                    
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
                            xpath=checker_data.input_file_xml_root.getpath(widthPoly.xml_element),
                            description=description,
                        )
                        # add 3d point
                        inertial_point = get_middle_point_xyz_at_height_zero_from_lane_by_s(road, laneSection.lane_section, lane, s_coordinate)
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
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_lane_width

    Description: Lane width must always be greater than zero or at the start/end point of a lanesection greater or equal to zero.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_lane_width check.")

    _check_all_roads(checker_data)
