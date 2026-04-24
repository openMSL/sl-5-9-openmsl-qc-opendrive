# SPDX-License-Identifier: MPL-2.0
# Copyright 2026, Envited OpenMSL
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import pytest

from typing import List

from qc_baselib import IssueSeverity, Result, StatusType
from openmsl_qc_opendrive.checks import semantic

from test_setup import *


@pytest.mark.parametrize(
    "target_file,issue_count,issue_xpath",
    [
        (
            "valid",
            0,
            [],
        ),
        (
            "invalid",
            5,
            [
                "/OpenDRIVE/road/objects/object[1]",
                "/OpenDRIVE/road/objects/object[2]",
                "/OpenDRIVE/road/objects/object[3]",
            ],
        ),
    ],
)
def test_road_object_size(
    target_file: str,
    issue_count: int,
    issue_xpath: List[str],
    monkeypatch,
) -> None:
    base_path = "tests/data/road_object_size/"
    target_file_name = f"road_object_size_{target_file}.xodr"
    rule_uid = semantic.road_object_size.RULE_UID
    issue_severity = IssueSeverity.WARNING

    target_file_path = os.path.join(base_path, target_file_name)
    create_test_config(target_file_path)
    launch_main(monkeypatch)
    check_issues(
        rule_uid,
        issue_count,
        issue_xpath,
        issue_severity,
        semantic.road_object_size.CHECKER_ID,
    )
    cleanup_files()


def test_road_object_size_outline_v1_5_reports_issues(monkeypatch) -> None:
    """In OpenDRIVE < 1.6, height/width/length are mandatory — outlined objects
    without those attributes should produce quality issues."""
    base_path = "tests/data/road_object_size/"
    target_file_path = os.path.join(
        base_path, "road_object_size_outline_v1_5.xodr"
    )
    rule_uid = semantic.road_object_size.RULE_UID
    checker_id = semantic.road_object_size.CHECKER_ID

    create_test_config(target_file_path)
    launch_main(monkeypatch)

    result = Result()
    result.load_from_file(REPORT_FILE_PATH)

    assert result.get_checker_status(checker_id) == StatusType.COMPLETED
    issues = result.get_issues_by_rule_uid(rule_uid)
    # Outlined object in v1.5 without height/width/length → exactly 2 issues
    # (one for missing size, one for missing height)
    assert len(issues) == 2
    assert any("height" in issue.description.lower() for issue in issues)

    cleanup_files()


def test_road_object_size_outline_v1_7_no_issues(monkeypatch) -> None:
    """In OpenDRIVE >= 1.6, outlined objects are allowed to omit height/width/length
    — the checker should skip them entirely (no issues)."""
    base_path = "tests/data/road_object_size/"
    target_file_path = os.path.join(
        base_path, "road_object_size_outline_v1_7.xodr"
    )
    rule_uid = semantic.road_object_size.RULE_UID
    checker_id = semantic.road_object_size.CHECKER_ID

    create_test_config(target_file_path)
    launch_main(monkeypatch)

    result = Result()
    result.load_from_file(REPORT_FILE_PATH)

    assert result.get_checker_status(checker_id) == StatusType.COMPLETED
    issues = result.get_issues_by_rule_uid(rule_uid)
    assert len(issues) == 0

    cleanup_files()


def test_road_object_size_no_outline_no_height_v1_7_reports_issue(monkeypatch) -> None:
    """In OpenDRIVE >= 1.6, non-outlined objects still need a height attribute.
    The else branch should fire and report a missing-height issue."""
    base_path = "tests/data/road_object_size/"
    target_file_path = os.path.join(
        base_path, "road_object_size_no_outline_no_height_v1_7.xodr"
    )
    rule_uid = semantic.road_object_size.RULE_UID
    checker_id = semantic.road_object_size.CHECKER_ID

    create_test_config(target_file_path)
    launch_main(monkeypatch)

    result = Result()
    result.load_from_file(REPORT_FILE_PATH)

    assert result.get_checker_status(checker_id) == StatusType.COMPLETED
    issues = result.get_issues_by_rule_uid(rule_uid)
    # Non-outlined object in v1.7 without height → 1 issue for missing height
    assert len(issues) == 1
    assert "height" in issues[0].description.lower()

    cleanup_files()