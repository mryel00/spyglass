import pytest
from unittest.mock import MagicMock


def test_parse_bindaddress(mocker):
    mock_libcamera = MagicMock()
    picamera2 = MagicMock()
    picamera2_encoders = MagicMock()
    picamera2_outputs = MagicMock()
    mocker.patch.dict('sys.modules', {
        'libcamera': mock_libcamera,
        'picamera2': picamera2,
        'picamera2.encoders': picamera2_encoders,
        'picamera2.outputs': picamera2_outputs,
    })

    from spyglass import cli
    args = cli.get_args(['-b', '127.0.0.1'])
    assert args.bindaddress == '127.0.0.1'
