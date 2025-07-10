# Checker bundle: openmsl_xodr_simulation_bundle

* Build version:  v1.0.0
* Description:    OpenDrive simulation checker bundle

## Parameters

* InputFile
* resultFile

## Checkers

### check_openmsl_xodr_road_geometry_length

* Description: Length of geometry elements shall be greater than epsilon and need to match with start of next element.

### check_openmsl_xodr_road_geometry_parampoly3_attributes

* Description: ParamPoly3 parameters @aU, @aV and @bV shall be zero, @bU shall be > 0.

### check_openmsl_xodr_road_min_length

* Description: Road Length shall be greater than epsilon.

### check_openmsl_xodr_crg_reference

* Description: check reference to OpenCRG files.

### check_openmsl_xodr_junction_connection_lane_link_id

* Description: Tlinked Lane shall exist in connected LaneSection.

### check_openmsl_xodr_junction_connection_lane_linkage_order

* Description: Lane Links of Junction Connections should be ordered from left to right.

### check_openmsl_xodr_junction_connection_road_linkage

* Description: Connection Roads need Predecessor and Successor. Connection Roads should be registered in Connection.

### check_openmsl_xodr_junction_driving_lanes_continue

* Description: check road lane links of juction connection - each driving lane of the incoming roads must have a connection in the junction.

### check_openmsl_xodr_road_lane_id_order

* Description: lane order should be continous and without gaps.

### check_openmsl_xodr_road_lane_link_id

* Description: linked Lane shall exist in connected LaneSection.

### check_openmsl_xodr_road_lane_property_sOffset

* Description: lane sOffsets (must be ascending, not too high) and sometimes be zero.

### check_openmsl_xodr_road_lane_type_none

* Description: Lane Type shall not be None.

### check_openmsl_xodr_road_lane_width

* Description: Lane width must always be greater than 0 or at the start/end point of a lanesection >= 0.

### check_openmsl_xodr_road_lanesection_min_length

* Description: Length of lanesections shall be greater than epsilon.

### check_openmsl_xodr_road_lanesection_s

* Description: Check starting sOffset of lanesections.

### check_openmsl_xodr_road_link_backward

* Description: check if linked elements are also linked to original element.

### check_openmsl_xodr_road_link_id

* Description: checks if linked Predecessor/Successor road/junction exist.

### check_openmsl_xodr_road_object_position

* Description: check if object position is valid - s value is in range of road length, t and zOffset in range.

### check_openmsl_xodr_road_object_size

* Description: check if object size is valid - width and length, radius and height in range.

### check_openmsl_xodr_road_signal_object_lane_linkage

* Description: Linked Lanes should exist and orientation should match with driving direction.

### check_openmsl_xodr_road_signal_position

* Description: check if signal position is valid - s value is in range of road length, t and zOffset in range.

### check_openmsl_xodr_road_signal_size

* Description: check if signal size is valid - width and height in range.

### check_openmsl_xodr_statistic

* Description: Prints some infos about OpenDrive file.

### check_openmsl_xodr_road_type_vs_speed_limit

* Description: Speed Limit of Lanes should match with road type.

