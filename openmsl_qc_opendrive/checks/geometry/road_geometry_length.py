# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_geometry_length"
CHECKER_DESCRIPTION = "Length of geometry elements shall be greater than epsilon and need to match with start of next element"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.geometry.length"

ROAD_GEOMETRY_MIN_LENGTH = 0.01
EPSILON_LENGTH = 0.01

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]
        roadLength = get_road_length(road)
        geometryList = get_road_plan_view_geometry_list(road)

        for geometry in geometryList:
            sGeom = get_s_from_geometry(geometry)
            lengthGeom = get_length_from_geometry(geometry)

            endLength = roadLength
            nextGeometry = geometry.getnext()
            if nextGeometry != None:
                endLength = get_s_from_geometry(nextGeometry)

            issue_descriptions = []
            diff = endLength - sGeom - lengthGeom
            if abs(diff) > EPSILON_LENGTH:
                issue_descriptions.append(f"road {roadID} Geometry {sGeom} has invalid length ({lengthGeom}) to next geometry or end (should be {endLength - sGeom})")
            if lengthGeom < ROAD_GEOMETRY_MIN_LENGTH:
                issue_descriptions.append(f"road {roadID} Geometry {sGeom} has invalid (too short) length {lengthGeom}")

            for description in issue_descriptions:
                # register issue
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
                    xpath=checker_data.input_file_xml_root.getpath(road),
                    description=description,
                )

                # add 3d point
                inertial_point = get_point_xyz_from_road_reference_line(road, sGeom)
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
    Rule ID: openmsl.net:xodr:1.4.0:road.geometry.length

    Description: Length of geometry elements shall be greater than epsilon and need to match with start of next element.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.geometry.length check.")

    _check_all_roads(checker_data)
