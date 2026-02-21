from __future__ import annotations

import plistlib
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "shortcuts" / "templates"

OBJECT_REPLACEMENT = "\ufffc"


def u() -> str:
    return str(uuid4()).upper()


def token_attachment(output_uuid: str, output_name: str) -> dict:
    return {
        "Value": {
            "OutputUUID": output_uuid,
            "Type": "ActionOutput",
            "OutputName": output_name,
        },
        "WFSerializationType": "WFTextTokenAttachment",
    }


def token_string_with_prefix(output_uuid: str, output_name: str, suffix: str) -> dict:
    return {
        "Value": {
            "string": f"{OBJECT_REPLACEMENT}{suffix}",
            "attachmentsByRange": {
                "{0, 1}": {
                    "OutputUUID": output_uuid,
                    "Type": "ActionOutput",
                    "OutputName": output_name,
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def show_result_text(output_uuid: str, output_name: str) -> dict:
    return {
        "Value": {
            "string": OBJECT_REPLACEMENT,
            "attachmentsByRange": {
                "{0, 1}": {
                    "OutputUUID": output_uuid,
                    "Type": "ActionOutput",
                    "OutputName": output_name,
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def action(identifier: str, params: dict) -> dict:
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": params,
    }


def build_capture_shortcut() -> dict:
    ask_uuid = u()
    screenshot_uuid = u()
    url_text_uuid = u()
    url_uuid = u()
    request_uuid = u()

    actions = [
        action(
            "is.workflow.actions.ask",
            {
                "UUID": ask_uuid,
                "WFAskActionPrompt": "AuraCap Backend Base URL",
                "WFAskActionDefaultAnswer": "https://your-domain.example",
                "WFInputType": "URL",
                "WFAllowsMultilineText": False,
            },
        ),
        action(
            "is.workflow.actions.takescreenshot",
            {
                "UUID": screenshot_uuid,
            },
        ),
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": url_text_uuid,
                "WFTextActionText": token_string_with_prefix(
                    ask_uuid,
                    "Provided Input",
                    "/v1/capture/raw?media_type=screenshot&source=ios_shortcut&locale=zh-CN&timezone=local&mime_type=image/png",
                ),
            },
        ),
        action(
            "is.workflow.actions.url",
            {
                "UUID": url_uuid,
                "Show-WFURLActionURL": True,
                "WFURLActionURL": token_attachment(url_text_uuid, "Text"),
            },
        ),
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": request_uuid,
                "Advanced": True,
                "WFHTTPMethod": "POST",
                "WFHTTPBodyType": "File",
                "ShowHeaders": False,
                "WFURL": token_attachment(url_uuid, "URL"),
                "WFRequestVariable": token_attachment(screenshot_uuid, "Screenshot"),
            },
        ),
        action(
            "is.workflow.actions.showresult",
            {
                "Text": show_result_text(request_uuid, "Contents of URL"),
            },
        ),
    ]

    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2700.0.4",
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 61440,
            "WFWorkflowIconStartColor": 2071128575,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowName": "AuraCap Capture",
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
    }


def build_voice_shortcut() -> dict:
    ask_uuid = u()
    record_uuid = u()
    url_text_uuid = u()
    url_uuid = u()
    request_uuid = u()

    actions = [
        action(
            "is.workflow.actions.ask",
            {
                "UUID": ask_uuid,
                "WFAskActionPrompt": "AuraCap Backend Base URL",
                "WFAskActionDefaultAnswer": "https://your-domain.example",
                "WFInputType": "URL",
                "WFAllowsMultilineText": False,
            },
        ),
        action(
            "is.workflow.actions.recordaudio",
            {
                "UUID": record_uuid,
                "WFRecordingStart": "Immediately",
                "WFRecordingEnd": "On Tap",
                "WFRecordingQuality": "Normal",
            },
        ),
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": url_text_uuid,
                "WFTextActionText": token_string_with_prefix(
                    ask_uuid,
                    "Provided Input",
                    "/v1/capture/raw?media_type=audio&source=ios_shortcut&locale=zh-CN&timezone=local&mime_type=audio/m4a",
                ),
            },
        ),
        action(
            "is.workflow.actions.url",
            {
                "UUID": url_uuid,
                "Show-WFURLActionURL": True,
                "WFURLActionURL": token_attachment(url_text_uuid, "Text"),
            },
        ),
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": request_uuid,
                "Advanced": True,
                "WFHTTPMethod": "POST",
                "WFHTTPBodyType": "File",
                "ShowHeaders": False,
                "WFURL": token_attachment(url_uuid, "URL"),
                "WFRequestVariable": token_attachment(record_uuid, "Audio Recording"),
            },
        ),
        action(
            "is.workflow.actions.showresult",
            {
                "Text": show_result_text(request_uuid, "Contents of URL"),
            },
        ),
    ]

    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2700.0.4",
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 61440,
            "WFWorkflowIconStartColor": 463140863,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowName": "AuraCap Voice",
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
    }


def write_unsigned(name: str, payload: dict) -> Path:
    out = TEMPLATE_DIR / f"{name}.shortcut"
    with out.open("wb") as f:
        plistlib.dump(payload, f, fmt=plistlib.FMT_XML, sort_keys=False)
    return out


def main() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    capture_unsigned = write_unsigned("AuraCap_Capture", build_capture_shortcut())
    voice_unsigned = write_unsigned("AuraCap_Voice", build_voice_shortcut())

    # Keep compatibility with tools that consume plist workflow source.
    capture_text = capture_unsigned.read_text(encoding="utf-8")
    voice_text = voice_unsigned.read_text(encoding="utf-8")
    (TEMPLATE_DIR / "AuraCap_Capture.plist").write_text(capture_text, encoding="utf-8")
    (TEMPLATE_DIR / "AuraCap_Voice.plist").write_text(voice_text, encoding="utf-8")


if __name__ == "__main__":
    main()
