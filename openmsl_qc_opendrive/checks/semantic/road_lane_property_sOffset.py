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

CHECKER_ID = "check_openmsl_xodr_road_lane_property_sOffset"
CHECKER_DESCRIPTION = "lane sOffsets must be ascending, should not exceed the length of road and must be zero for first element of width/border"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_lane_property_sOffset"

LENGTH_EPSILON = 0.0000001

def checkLanePropSOffsets(road: etree._Element, lane: etree._Element, laneSection: models.LaneSectionWithLength, lanePropertyName: str, checker_data: models.CheckerData):
    roadID = road.attrib["id"]
    laneID = int(lane.attrib["id"])
    startOfLaneSection = utils.get_s_from_lane_section(laneSection.lane_section)
    prevSOffset = float(-1.0)
    for laneProperty in lane.findall(lanePropertyName):
        sOffset = float(laneProperty.attrib["sOffset"])
        issue_descriptions = []
        if sOffset < 0.0:
            sOffset = max(0.0, prevSOffset)                  # no issue as it is checked by schema already
        elif sOffset <= prevSOffset and lanePropertyName != "access":
            issue_descriptions.append(f"road {roadID} has invalid (not ascending) sOffset:{str(sOffset)} in laneSection s={startOfLaneSection} lane={str(laneID)} {lanePropertyName}")
        elif (lanePropertyName == "width" or lanePropertyName == "border") and prevSOffset == -1.0 and sOffset != 0.0:
            issue_descriptions.append(f"road {roadID} has invalid (first element not zero) sOffset:{str(sOffset)} in laneSection s={startOfLaneSection} lane={str(laneID)} {lanePropertyName}")
        elif sOffset - laneSection.length > LENGTH_EPSILON:
            if sOffset != 0.0:                              # otherwise no issue as this is checked by road_lanesection_s
                issue_descriptions.append(f"road {roadID} has invalid (too high) sOffset:{str(sOffset)} in laneSection s={startOfLaneSection} lane={str(laneID)} {lanePropertyName}")
                sOffset = laneSection.length
        prevSOffset = sOffset

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
                xpath=checker_data.input_file_xml_root.getpath(laneProperty),
                description=description,
            )
            # add 3d point
            inertial_point = utils.get_middle_point_xyz_at_height_zero_from_lane_by_s(road, laneSection.lane_section, lane, startOfLaneSection + sOffset)
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


def checkLaneSOffsets(road: etree._Element, laneSection: models.LaneSectionWithLength, side: str, checker_data: models.CheckerData):
    laneSide = laneSection.lane_section.find(side)
    if laneSide is None:
        return                              # lanesection has no lanes on this side
    
    for lane in laneSide.findall("lane"):
         if side != "center":
             checkLanePropSOffsets(road, lane, laneSection, "width", checker_data)
             checkLanePropSOffsets(road, lane, laneSection, "material", checker_data)
             checkLanePropSOffsets(road, lane, laneSection, "speed", checker_data)
             checkLanePropSOffsets(road, lane, laneSection, "access", checker_data)
         checkLanePropSOffsets(road, lane, laneSection, "border", checker_data)
         checkLanePropSOffsets(road, lane, laneSection, "height", checker_data)
         checkLanePropSOffsets(road, lane, laneSection, "roadMark", checker_data)
         checkLanePropSOffsets(road, lane, laneSection, "rule", checker_data)

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = utils.get_roads(checker_data.input_file_xml_root)

    for road in roads:
        laneSections = utils.get_sorted_lane_sections_with_length_from_road(road)
        for laneSection in laneSections:
            checkLaneSOffsets(road, laneSection, "left", checker_data)
            checkLaneSOffsets(road, laneSection, "right", checker_data)
            checkLaneSOffsets(road, laneSection, "center", checker_data)

def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_lane_property_sOffset

    Description: lane sOffsets must be ascending, should not exceed the length of road and must be zero for first element of width/border.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_lane_property_sOffset check.")

    _check_all_roads(checker_data)
