# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_lanesection_s"
CHECKER_DESCRIPTION = "Check starting sOffset of lanesections"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.lanesection_s"

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_roads(checker_data.input_file_xml_root)

    for road in roads:
        roadID = road.attrib["id"]
        roadLength = get_road_length(road)
        laneSections = get_lane_sections(road)
        prevLaneSectionStart = -1.0
        for laneSection in laneSections:
            s_coordinate = get_s_from_lane_section(laneSection)
            description = ""
            if s_coordinate > roadLength:
                description = f"road {roadID} has laneSection with invalid (too high) s={s_coordinate} (roadLength={roadLength})"
            elif laneSections.index(laneSection) == 0 and s_coordinate != 0.0:
                description = f"road {roadID} has laneSection with invalid s={s_coordinate} (first laneSection needs to start at s=0.0)"
            elif prevLaneSectionStart >= s_coordinate:
                description = f"road {roadID} has laneSection with invalid (not ascending) s={s_coordinate}"
            prevLaneSectionStart = s_coordinate

            if description != "":
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
                    xpath=checker_data.input_file_xml_root.getpath(laneSection),
                    description=description,
                )


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.lanesection_s

    Description: Check starting sOffset of lanesections.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.lanesection_s check.")

    _check_all_roads(checker_data)
