# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_road_lane_link_id"
CHECKER_DESCRIPTION = "linked Lane shall exist in connected LaneSection"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:road.semantic.road_lane_link_id"

def _check_all_roads(checker_data: models.CheckerData) -> None:
    roads = get_road_id_map(checker_data.input_file_xml_root)

    for roadID, road in roads.items():
        predRoad = get_road_linkage(road, models.LinkageTag.PREDECESSOR)
        succRoad = get_road_linkage(road, models.LinkageTag.SUCCESSOR)
        
        laneSection_list = get_sorted_lane_sections_with_length_from_road(road)
        index = 0
        for laneSection in laneSection_list:
            s_coordinate = get_s_from_lane_section(laneSection.lane_section)

            prevLaneSection = None
            if index == 0 and predRoad:
                connectedSection = get_contact_lane_section_from_linked_road(predRoad, roads)
                if connectedSection:
                    prevLaneSection = connectedSection.lane_section
            elif index > 0:
                prevLaneSection = laneSection_list[index - 1].lane_section

            succLaneSection = None
            if index + 1 == len(laneSection_list) and succRoad:
                connectedSection = get_contact_lane_section_from_linked_road(succRoad, roads)
                if connectedSection:
                    succLaneSection = connectedSection.lane_section
            elif index + 1 < len(laneSection_list):
                succLaneSection = laneSection_list[index + 1].lane_section

            index = index + 1
            lane_list = get_left_and_right_lanes_from_lane_section(laneSection.lane_section)
            for lane in lane_list:
                issue_descriptions = []
                lane_id = lane.get("id")

                predecessors = get_predecessor_lane_ids(lane)
                for predecessor in predecessors:
                    if prevLaneSection is None:
                        issue_descriptions.append(f"road {roadID} LaneSection {s_coordinate} Lane {lane_id} has invalid lane linkage : lane predecessor not found")
                    else:
                        connectedLane = get_lane_from_lane_section(prevLaneSection, predecessor)
                        if connectedLane is None:
                            issue_descriptions.append(f"road {roadID} LaneSection {s_coordinate} Lane {lane_id} has invalid lane linkage : lane predecessor not found")

                successors = get_successor_lane_ids(lane)
                for successor in successors:
                    if succLaneSection is None:
                        issue_descriptions.append(f"road {roadID} LaneSection {s_coordinate} Lane {lane_id} has invalid lane linkage : lane successor not found")
                    else:
                        connectedLane = get_lane_from_lane_section(succLaneSection, successor)
                        if connectedLane is None:
                            issue_descriptions.append(f"road {roadID} LaneSection {s_coordinate} Lane {lane_id} has invalid lane linkage : lane successor not found")

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
                        xpath=checker_data.input_file_xml_root.getpath(lane),
                        description=description,
                    )

                    if s_coordinate is None:
                        continue

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
    Rule ID: openmsl.net:xodr:1.4.0:road.semantic.road_lane_link_id

    Description: linked Lane shall exist in connected LaneSection.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.semantic.road_lane_link_id check.")

    _check_all_roads(checker_data)
