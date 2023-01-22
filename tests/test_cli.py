from unittest.mock import MagicMock, ANY

AF_SPEED_ENUM_FAST = 2
AF_MODE_ENUM_MANUAL = 3


def test_parse_bindaddress(mocker):
    mock_libraries(mocker)

    from spyglass import cli
    args = cli.get_args(['-b', '1.2.3.4'])
    assert args.bindaddress == '1.2.3.4'


def test_parse_port(mocker):
    mock_libraries(mocker)

    from spyglass import cli
    args = cli.get_args(['-p', '123'])
    assert args.port == 123


def test_parse_resolution(mocker):
    mock_libraries(mocker)

    from spyglass import cli
    args = cli.get_args(['-r', '100x200'])
    assert args.resolution == '100x200'


def test_split_resolution(mocker):
    mock_libraries(mocker)

    from spyglass import cli
    (width, height) = cli.split_resolution('100x200')
    assert width == 100
    assert height == 200


def test_init_camera(mocker):
    mock_libraries(mocker)
    mocker.patch('spyglass.camera.init_camera')
    mocker.patch('spyglass.server.run_server')
    mocker.patch('libcamera.controls.AfModeEnum.Manual', AF_MODE_ENUM_MANUAL)
    mocker.patch('libcamera.controls.AfSpeedEnum.Fast', AF_SPEED_ENUM_FAST)
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-r', '100x200',
        '-f', '10',
        '-af', 'manual',
        '-s', 'fast'
    ])
    spyglass.camera.init_camera.assert_called_once_with(100, 200, 10, AF_MODE_ENUM_MANUAL, 0.0, AF_SPEED_ENUM_FAST)


def test_start_server(mocker):
    mock_libraries(mocker)
    mocker.patch('spyglass.camera.init_camera')
    mocker.patch('spyglass.server.run_server')
    from spyglass import cli
    import spyglass.server
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url'
    ])
    # run_server(bind_address, port, output, stream_url, snapshot_url)StreamingOutput
    spyglass.server.run_server.assert_called_once_with('1.2.3.4', 1234, ANY, 'streaming-url', 'snapshot-url')


def test_start_recording(mocker):
    mock_libraries(mocker)
    mocker.patch('spyglass.camera.init_camera')
    mocker.patch('spyglass.server.run_server')
    from spyglass import cli
    import spyglass.server
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url'
    ])
    # run_server(bind_address, port, output, stream_url, snapshot_url)StreamingOutput
    spyglass.server.run_server.assert_called_once_with('1.2.3.4', 1234, ANY, 'streaming-url', 'snapshot-url')


def mock_libraries(mocker):
    mock_libcamera = MagicMock()
    mock_picamera2 = MagicMock()
    mock_picamera2_encoders = MagicMock()
    mock_picamera2_outputs = MagicMock()
    mocker.patch.dict('sys.modules', {
        'libcamera': mock_libcamera,
        'picamera2': mock_picamera2,
        'picamera2.encoders': mock_picamera2_encoders,
        'picamera2.outputs': mock_picamera2_outputs,
    })
