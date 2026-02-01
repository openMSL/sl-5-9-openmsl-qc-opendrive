import logging

from qc_baselib import IssueSeverity

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_statistic"
CHECKER_DESCRIPTION = "Prints some infos about OpenDRIVE file"
CHECKER_PRECONDITIONS = set()
RULE_UID = "openmsl.net:xodr:1.4.0:statistic"

def calc_frequency(checker_data: models.CheckerData) -> None:
    issue_descriptions = []

    roads = get_roads(checker_data.input_file_xml_root)
    issue_descriptions.append(f"Number of roads: {len(roads)}")

    junctions = get_junctions(checker_data.input_file_xml_root)
    issue_descriptions.append(f"Number of junctions: {len(junctions)}")

    # network length
    roadLengths = 0.0
    for road in roads:
        roadLengths += get_road_length(road)
        float(road.attrib["length"])
    issue_descriptions.append(f"RoadNetwork length: {roadLengths} m")    
    
    #signals
    signals = checker_data.input_file_xml_root.findall(f".//signal")
    issue_descriptions.append(f"Number of signals: {len(signals)}")
    signal_types = dict()
    for signal in signals:
        type_str = f'{signal.attrib["type"]}_{signal.attrib["subtype"]}'
        if type_str in signal_types:
            signal_types[type_str] = signal_types[type_str] + 1
        else:
            signal_types[type_str] = 1
    
    sorted_signal_type = sorted(signal_types.items())
    for key, count in sorted_signal_type:
        issue_descriptions.append(f"Numer of Signal type {key}: {count}")

    # objects
    objects = checker_data.input_file_xml_root.findall(f".//object")
    issue_descriptions.append(f"Number of objects: {len(objects)}")
    object_types = dict()
    for object in objects:
        type_str = f'{object.attrib["type"]}'
        if type_str in object_types:
            object_types[type_str] = object_types[type_str] + 1
        else:
            object_types[type_str] = 1
    
    sorted_object_type = sorted(object_types.items())            
    for key, count in sorted_object_type:
        issue_descriptions.append(f"Numer of object type {key}: {count}")

    for description in issue_descriptions:
        # register issues
        issue_id = checker_data.result.register_issue(
            checker_bundle_name=constants.BUNDLE_NAME,
            checker_id=CHECKER_ID,
            description=description,
            level=IssueSeverity.INFORMATION,
            rule_uid=RULE_UID,
        )
        # add xml location
        checker_data.result.add_xml_location(
            checker_bundle_name=constants.BUNDLE_NAME,
            checker_id=CHECKER_ID,
            issue_id=issue_id,
            xpath=checker_data.input_file_xml_root.getpath(roads[0]),
            description=description,
        )


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:statistic

    Description: Prints some infos about OpenDRIVE file.

    Severity: INFORMATION

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing statistic check.")

    calc_frequency(checker_data)
