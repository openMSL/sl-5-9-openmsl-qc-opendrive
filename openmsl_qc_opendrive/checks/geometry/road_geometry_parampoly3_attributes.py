# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_geometry_parampoly3_attributes"
CHECKER_DESCRIPTION = "ParamPoly3 parameters @aU, @aV and @bV shall be zero, @bU shall be > 0"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.geometry.parampoly3.attributes"

TOLERANCE_THRESHOLD_BV = 0.001

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]

        geometry_list = get_road_plan_view_geometry_list(road)
        for geometry in geometry_list:
            length = get_length_from_geometry(geometry)
            if length is None:
                continue

            param_poly3 = get_arclen_param_poly3_from_geometry(geometry)
            if param_poly3 is None:
                param_poly3 = get_normalized_param_poly3_from_geometry(geometry)
                if param_poly3 is None:
                    continue

            s_coordinate = get_s_from_geometry(geometry)

            issue_descriptions = []
            if param_poly3.u.a != 0.0:                
                issue_descriptions.append(f"road {roadID} has invalid paramPoly3 : aU != 0.0 ({param_poly3.u.a}) at s={s_coordinate}")

            if param_poly3.v.a != 0.0:
                issue_descriptions.append(f"road {roadID} has invalid paramPoly3 : aV != 0.0 ({param_poly3.v.a}) at s={s_coordinate}")

            if abs(param_poly3.v.b) > TOLERANCE_THRESHOLD_BV:
                issue_descriptions.append(f"road {roadID} has invalid paramPoly3 : abs(bV) > {TOLERANCE_THRESHOLD_BV} ({param_poly3.v.b}) at s={s_coordinate}")              

            if param_poly3.u.b <= 0.0:
                issue_descriptions.append(f"road {roadID} has invalid paramPoly3 : bU <= 0.0 ({param_poly3.u.b}) at s={s_coordinate}")

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
                    xpath=checker_data.input_file_xml_root.getpath(geometry),
                    description=description,
                )

                if s_coordinate is None:
                    continue

                s_coordinate += length / 2.0

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
    Rule ID: openmsl.net:xodr:1.4.0:road.geometry.parampoly3.attributes

    Description: ParamPoly3 parameters @aU, @aV and @bV shall be zero, @bU shall be > 0.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.geometry.parampoly3.attributes check.")

    _check_all_roads(checker_data)
