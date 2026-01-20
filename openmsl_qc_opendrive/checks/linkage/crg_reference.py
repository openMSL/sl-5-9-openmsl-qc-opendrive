# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import os

from qc_baselib import IssueSeverity
from pathlib import Path

from openmsl_qc_opendrive import constants
from qc_opendrive.base.utils import *

CHECKER_ID = "check_openmsl_xodr_crg_reference"
CHECKER_DESCRIPTION = "check reference to OpenCRG files"
CHECKER_PRECONDITIONS = ""#basic_preconditions.CHECKER_PRECONDITIONS
RULE_UID = "openmsl.net:xodr:1.4.0:road.linkage.crg_reference"

def _check_references(checker_data: models.CheckerData) -> None:

    crgs = checker_data.input_file_xml_root.findall(f".//CRG")
    for crg in crgs:
        crg_file = Path(crg.attrib['file'])
        abs_path = os.path.dirname(checker_data.xml_file_path)
        abs_file = Path(os.path.abspath(os.path.join(abs_path, crg_file)))
        if not abs_file.exists():
            description = f"CRG file {abs_file} not exist."
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
                xpath=checker_data.input_file_xml_root.getpath(crg),
                description=description,
            )


def check_rule(checker_data: models.CheckerData) -> None:
    """
    Rule ID: openmsl.net:xodr:1.4.0:road.linkage.crg_reference

    Description: check reference to OpenCRG files.

    Severity: WARNING

    Version range: [1.4.0, )

    Remark:
        TODO
    """
    logging.info("Executing road.linkage.crg_reference.")

    _check_references(checker_data)
