"""XML report rendering."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from pyepubcheck.result import ValidationReport


def render_xml_report(report: ValidationReport) -> str:
    root = ET.Element("report", version=report.version, profile=report.profile)
    root.set("title", report.metadata.title)
    messages = ET.SubElement(root, "messages")
    for message in report.messages:
        node = ET.SubElement(
            messages, "message", id=message.id, severity=message.severity.value
        )
        node.text = message.message
    return ET.tostring(root, encoding="unicode")
