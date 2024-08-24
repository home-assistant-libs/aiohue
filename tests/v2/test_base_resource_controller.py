from aiohue import HueBridgeV2
from aiohue.v2.controllers.sensors import ButtonController, RelativeRotaryController


def test_handle_last_event_backwards_compatibility_for_button():
    evt_data = {"button": {"last_event": "initial_press"}}

    bridge = HueBridgeV2("127.0.0.1", "fake")
    button_controller = ButtonController(bridge)
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("button", {}).get("button_report", {}).get("event")
        == "initial_press"
    )

    evt_data = {
        "button": {
            "last_event": "initial_press",
            "button_report": {"event": "short_release"},
        }
    }

    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("button", {}).get("button_report", {}).get("event")
        == "short_release"
    )

    evt_data = {"button": {}}

    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert evt_data.get("button", {}).get("button_report") is None


def test_handle_last_event_backwards_compatibility_for_relative_rotary():
    evt_data = {
        "relative_rotary": {
            "last_event": {
                "action": "start",
                "rotation": {"direction": "clock_wise", "steps": 1, "duration": 800},
            }
        }
    }

    bridge = HueBridgeV2("127.0.0.1", "fake")
    rotary_controller = RelativeRotaryController(bridge)
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("relative_rotary", {}).get("rotary_report", {}).get("action")
        == "start"
    )
    assert evt_data.get("relative_rotary", {}).get("rotary_report", {}).get(
        "rotation"
    ) == evt_data.get("relative_rotary", {}).get("last_event", {}).get("rotation")

    evt_data = {
        "relative_rotary": {
            "last_event": {
                "action": "start",
                "rotation": {"direction": "clock_wise", "steps": 1, "duration": 800},
            },
            "rotary_report": {
                "action": "repeat",
                "rotation": {
                    "direction": "counter_clock_wise",
                    "steps": 1,
                    "duration": 800,
                },
            },
        }
    }

    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("relative_rotary", {}).get("rotary_report", {}).get("action")
        == "repeat"
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("direction")
        == "counter_clock_wise"
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("steps")
        == 1
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("duration")
        == 800
    )

    evt_data = {"relative_rotary": {}}

    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert evt_data.get("relative_rotary", {}).get("rotary_report") is None
