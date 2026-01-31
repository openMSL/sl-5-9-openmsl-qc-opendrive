# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from openmsl_qc_opendrive.checks.basic import (
    valid_xml_document,
    root_tag_is_opendrive,
    fileheader_is_present,
    version_is_defined,
)

CHECKER_PRECONDITIONS = {
    valid_xml_document.CHECKER_ID,
    root_tag_is_opendrive.CHECKER_ID,
    fileheader_is_present.CHECKER_ID,
    version_is_defined.CHECKER_ID
}
