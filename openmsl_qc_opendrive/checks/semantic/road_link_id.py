# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_link_id"
CHECKER_DESCRIPTION = "checks if linked Predecessor/Successor road/junction exist"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_link_id"

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_road_id_map(checker_data.input_file_xml_root)
    junctions = get_junction_id_map(checker_data.input_file_xml_root)

    for roadID, road in roads.items():
        issue_descriptions = []
        predRoad = get_road_linkage(road, models.LinkageTag.PREDECESSOR)
        if predRoad:
            linked_road = roads.get(predRoad.id)
            if linked_road is None:
                issue_descriptions.append(f"predecessor road (id={predRoad.id}) of road {roadID} not found!")

        succRoad = get_road_linkage(road, models.LinkageTag.SUCCESSOR)
        if succRoad:
            linked_road = roads.get(succRoad.id)
            if linked_road is None:
                issue_descriptions.append(f"successor road (id={succRoad.id}) of road {roadID} not found!")

        predJunction = get_linked_junction_id(road, models.LinkageTag.PREDECESSOR)
        if predJunction:
            linked_junction = junctions.get(predJunction)
            if linked_junction is None:
                issue_descriptions.append(f"predecessor junction (id={predJunction}) of road {roadID} not found!")

        succJunction = get_linked_junction_id(road, models.LinkageTag.SUCCESSOR)
        if succJunction:
            linked_junction = junctions.get(succJunction)
            if linked_junction is None:
                issue_descriptions.append(f"successor junction (id={succJunction}) of road {roadID} not found!")        

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
                xpath=checker_data.input_file_xml_root.getpath(road),
                description=description,
            )

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_link_id

    Description: checks if linked Predecessor/Successor road/junction exist.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_link_id check.")

    _check_all_roads(checker_data)
