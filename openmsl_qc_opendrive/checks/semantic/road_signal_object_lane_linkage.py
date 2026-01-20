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

CHECKER_ID = "check_openmsl_xodr_road_signal_object_lane_linkage"
CHECKER_DESCRIPTION = "Linked Lanes should exist and orientation should match with driving direction"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.signal_object_lane_linkage"

def check_validity(signal_object: etree._Element, traffic_rule: models.TrafficHandRule, road: etree._Element, checker_data: models.CheckerData) -> None:
    validity = signal_object.find("validity")
    if validity is None:                            # no valitidy, so nothing to check
        return

    # check if lanes exist at signal/object position
    id = signal_object.attrib['id']
    sValue = to_float(signal_object.attrib['s'])
    tValue = to_float(signal_object.attrib['t'])
    fromLane = validity.attrib['fromLane']
    toLane = validity.attrib['toLane']
    laneSection = get_lane_section_from_road_by_s(road, sValue)
    issue_descriptions = []
    if fromLane == '0' or toLane == '0':
        issue_descriptions.append(f"lane validity of {signal_object.tag} {id} references to invalid lane 0")
    if fromLane != '0' and get_lane_from_lane_section(laneSection, to_int(fromLane)) is None:
        issue_descriptions.append(f"lane validity of {signal_object.tag} {id} references to not existing fromLane {fromLane}")
    if toLane != '0' and get_lane_from_lane_section(laneSection, to_int(toLane)) is None:
        issue_descriptions.append(f"lane validity of {signal_object.tag} {id} references to not existing toLane {toLane}")

    # check if from is lower                                # TODO check if from is on the inner side of to. Also if orientation is both?
    #if int(fromLane) > int(toLane):
    #    message = f"lane validity of {signal_object.tag} {id} invalid. fromLane needs to be lower than or equal to toLane"
    #    checker.gen_issue(IssueLevel.WARNING, message, create_location_from_element(signal_object))
    
    # check orientation
    orientation = signal_object.attrib['orientation']
    error = ""
    if traffic_rule == models.TrafficHandRule.RHT:                   # right hand traffic
        if orientation == '+':                  # negative lane ids
            if to_int(fromLane) > 0 or to_int(toLane) > 0:
                error = "negative"
        elif orientation == '-':                # positve lane ids
            if to_int(fromLane) < 0 or to_int(toLane) < 0:
                error = "positive"
    elif traffic_rule == models.TrafficHandRule.LHT:                 # left hand traffic
        if orientation == '-':                  # negative lane ids
            if to_int(fromLane) > 0 or to_int(toLane) > 0:
                error = "negative"
        elif orientation == '+':                # positve lane ids
            if to_int(fromLane) < 0 or to_int(toLane) < 0:
                error = "positive"
    if error != "":
        issue_descriptions.append(f"lane validity of {signal_object.tag} {id} should be {error} for {traffic_rule} with orientation {orientation}")

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
            xpath=checker_data.input_file_xml_root.getpath(signal_object),
            description=description,
        )

        # add 3d point
        inertial_point = get_point_xyz_from_road(road, sValue, tValue, 0.0)
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
        rule = get_traffic_hand_rule_from_road(road)

        for signal in road.findall("./signals/signal"):        
            check_validity(signal, rule, road, checker_data)
        for signal in road.findall("./signals/signalReference"):
            check_validity(signal, rule, road, checker_data)
        for object in road.findall("./objects/object"):
            check_validity(object, rule, road, checker_data)
        for object in road.findall("./objects/objectReference"):
            check_validity(object, rule, road, checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.signal_object_lane_linkage

    Description: Linked Lanes should exist and orientation should match with driving direction.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.signal_object_lane_linkage check.")

    _check_all_roads(checker_data)
