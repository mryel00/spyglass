# Spyglass

> **Please note that this project is in a very early stage. Use at your own risk. Think about contributing to the project
if you find that something is not working, and you are able to fix it. Every contribution is appreciated.**

A simple mjpeg server for Picamera2.

With Spyglass you are able to stream videos from a camera that is supported by [libcamera](http://libcamera.org) like
the [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/).

Current version: 0.10.2

## Prerequisites

-   Raspberry Pi OS Bullseye
-   [Picamera2](https://github.com/raspberrypi/picamera2) - Already installed on Raspberry Pi OS Bullseye
-   Python 3.8+
-   A camera supported by libcamera and connected to the Raspberry Pi

## Quick Start

The server can be started with

```shell
./run.py
```

This will start the server with the following default configuration:

-   Address the server binds to: 0.0.0.0
-   Port: 8080
-   Resolution: 640x480
-   Framerate: 15fps
-   Stream URL: /stream
-   Snapshot URL: /snapshot

## Configuration

On startup the following arguments are supported:

| Argument                 | Description                                                                                         | Default      |
| ------------------------ | --------------------------------------------------------------------------------------------------- | ------------ |
| `-b`, `--bindaddress`    | Address where the server will listen for new incoming connections.                                  | `0.0.0.0`    |
| `-p`, `--port`           | Port where the server will listen for new incoming connections.                                     | `8080`       |
| `-r`, `--resolution`     | Resolution of the captured frames. This argument expects the format <width>x<height>                | `640x480`    |
| `-f`, `--fps`            | Framerate in frames per second (fps).                                                               | `15`         |
| `-st`, `--stream_url`    | Sets the URL for the mjpeg stream.                                                                  | `/stream`    |
| `-sn`, `--snapshot_url`  | Sets the URL for snapshots (single frame of stream).                                                | `/snapshot`  |
| `-af`, `--autofocus`     | Autofocus mode. Supported modes: `manual`, `continuous`                                              | `continuous` |
| `-l`, `--lensposition`   | Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. Only used with Autofocus manual | `0.0`        |
| `-s`, `--autofocusspeed` | Autofocus speed. Supported values: `normal`, `fast`. Only used with Autofocus continuous            | `normal`     |

Starting the server without any argument is the same as

```shell
./run.py -b 0.0.0.0 -p 8080 -r 640x480 -f 15 -st '/stream' -sn '/snapshot' -af continuous -l 0.0 -s normal
```

The stream can then be accessed at `http://<IP of the server>:8080/stream`

### Maximum resolution

Please note that the maximum recommended resolution is 1920x1080 (16:9).

The absolute maximum resolution is 1920x1920. If you choose a higher resolution spyglass may crash.

## Using Spyglass with Mainsail

If you want to use Spyglass as a webcam source for [Mainsail]() add a webcam with the following configuration:

-   URL Stream: `/webcam/stream`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `V4L-MJPEG`

## Install as application

If you want to install Spyglass globally on your machine you can use `python -m pip install .` to do so.

## Install and run as a service

### Install

Quite simple:

```bash
cd ~/spyglass
make install
```

This will ask you for your `sudo` password.\
After install is done, please reboot to ensure service starts properly

To uninstall the service simply use

```bash
cd ~/spyglass
make uninstall
```

### Configuration

You should find a configuration file in `~/printer_data/config/spyglass.conf`.

Please see [spyglass.conf](resources/spyglass.conf) for an example

### Restart the service

To restart the service use `systemctl`:

```shell
sudo systemctl restart spyglass
```

## Start Developing

If you want to setup your environment for development perform the following steps:

Setup your Python virtual environment:
```shell
python -m venv .venv                  # Create a new virtual environment
. .venv/bin/activate                  # Activate virtual environment
python -m pip install --upgrade pip   # Upgrade PIP to the current version
pip install -r requirements.txt       # Install application dependencies
pip install -r requirements-test.txt  # Install test dependencies
pip install -r requirements-dev.txt   # Install development dependencies
```

The project uses [commitizen](https://github.com/commitizen-tools/commitizen) to check commit messages to comply with
[Conventional Commits](http://conventionalcommits.org). When installing the development dependencies git-hooks will be
set up to check commit messages pre commit.

### Problems when Committing to your Branch

 You may get the following error message when you try to push to your branch:
 ```
 fatal: ambiguous argument 'origin/HEAD..HEAD': unknown revision or path not in the working tree.
 Use '--' to separate paths from revisions, like this:
 'git <command> [<revision>...] -- [<file>...]'
 ```
 This error occurs when your HEAD branch is not properly set ([Stack Overflow](https://stackoverflow.com/a/8841024))
 To fix this run the following command:
 ```shell
 git remote set-head origin -a
 ```
