# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from enum import Enum

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_junction_connection_lane_linkage_order"
CHECKER_DESCRIPTION = "Lane Links of Junction Connections should be ordered from left to right"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.junction_connection_lane_linkage_order"

def _check_all_junctions(checker_data: models.CheckerData) -> None:
    invalid = 999
    junctions = get_junctions(checker_data.input_file_xml_root)
    for junction in junctions:
        junctionID = junction.attrib["id"]
        connections = get_connections_from_junction(junction)
        for connection in connections:
            lastFrom = invalid
            connectionID = connection.attrib["id"]
            laneLinks = get_lane_links_from_connection(connection)
            issue_descriptions = []
            for laneLink in laneLinks:
                laneFrom = get_from_attribute_from_lane_link(laneLink)
                if lastFrom != invalid and laneFrom >= lastFrom:
                    issue_descriptions.append(f"junction {junctionID} Connection {connectionID} has invalid lane order for laneFrom: {laneFrom}")
                    break
                lastFrom = laneFrom

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
                    xpath=checker_data.input_file_xml_root.getpath(laneLink),
                    description=description,
                )


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.junction_connection_lane_linkage_order

    Description: Lane Links of Junction Connections should be ordered from left to right

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.junction_connection_lane_linkage_order check.")

    _check_all_junctions(checker_data)
