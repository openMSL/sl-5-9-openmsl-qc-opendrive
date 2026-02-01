# openmsl-qc-opendrive

This project extends the ASAM QualityChecker (https://www.asam.net/standards/asam-quality-checker/) with simulation-based checks for ASAM OpenDRIVE (https://www.asam.net/standards/detail/opendrive/).
This project implements the [OpenMSL OpenDRIVE Checker Bundle](checker_bundle_doc.md).

## Installation

openmsl-qc-opendrive can be installed using pip or from source.

### Installation using pip

openmsl-qc-opendrive can be installed using pip, so that it can be used as a library or
as an application.

**From PyPi**

```bash
pip install openmsl-qc-opendrive
```

**From GitHub repository**

```bash
pip install openmsl-qc-opendrive@git+https://github.com/openMSL/sl-5-9-openmsl_qc_opendrive@main
```

The above command will install `openmsl-qc-opendrive` from the `main` branch. If you want to install `openmsl-qc-opendrive` from another branch or tag, replace `@main` with the desired branch or tag.

For further installation options, please consult the ASAM QualityChecker Bundle manual https://github.com/asam-ev/qc-opendrive?tab=readme-ov-file#installation-and-usage. 
This also explains how to use the manifest, the configuration file, and how to run the test.

## Usage

```bash
openmsl_qc_opendrive -c config_file.xml
```

For further usage options, please consult the ASAM QualityChecker Framework manual https://github.com/asam-ev/qc-framework/blob/main/doc/manual/file_formats.md#configuration-file-xml

## Configuration

An example template for a configuration file with all tests can be found in `openmsl_qc_config_xodr.xml`. You must specify your OpenDRIVE file in Param `InputFile`.
You can define individual checks in the `CheckerBundle` area.
In the `ReportModule` area, you specify the type of report and the file names.

## Output 

We recommend output in xqar format. You can find information about this here https://github.com/asam-ev/qc-framework/blob/main/doc/manual/file_formats.md#result-file-xqar
You can view the format using the ReportGUI tool, see https://github.com/asam-ev/qc-framework/blob/main/doc/manual/using_the_framework.md