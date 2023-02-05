# Spyglass

---

**Please note that this project is in a very early stage. Use at your own risk. Think about contributing to the project
if you find that something is not working, and you are able to fix it. Every contribution is appreciated.**

---

A simple mjpeg server for Picamera2.

With Spyglass you are able to stream videos from a camera that is supported by [libcamera](http://libcamera.org) like
the [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/).

## Prerequisites

-   Raspberry Pi OS Bullseye
-   [Picamera2](https://github.com/raspberrypi/picamera2) - Already installed on Raspberry Pi OS Bullseye
-   Python 3
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

## Using Spyglass with Mainsail

If you ant to use Spyglass as a webcam source for [Mainsail]() add a webcam with the following configuration:

-   URL Stream: `/webcam/stream`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `V4L-MJPEG`

## Install as application

If you want to install Spyglass globally on your machine you can use `python -m pip install .` to do so.

## Install as a service

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

## Configuration if run as service

You should find a configuration file in ~/printer_data/config/spyglass.conf.\

Please see [spyglass.conf](resources/spyglass.conf) for an example
