# Spyglass

A simple mjpeg server for Picamera2.

With Spyglass you are able to stream videos from a camera that is supported by [libcamera](http://libcamera.org) like
the [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/).

## Prerequisites

* Raspberry Pi OS Bullseye
* [Picamera2](https://github.com/raspberrypi/picamera2) - Already installed on Raspberry Pi OS Bullseye
* Python 3
* A camera supported by libcamera and connected to the Raspberry Pi

## Quick Start

The server can be started with
```shell
./spyglass.py
```

This will start the server with the following default configuration:
* Address the server binds to: 0.0.0.0
* Port: 8080
* Resolution: 640x480
* Framerate: 15fps

## Configuration

On startup the following arguments are supported:

| Argument              | Description                                                                          | Default   |
|-----------------------|--------------------------------------------------------------------------------------|-----------|
| `-b`, `--bindaddress` | Address where the server will listen for new incoming connections.                   | `0.0.0.0` |
| `-p`, `--port`        | Port where the server will listen for new incoming connections.                      | `8080`    |
| `-r`, `--resolution`  | Resoultion of the captured frames. This argument expects the format <width>x<height> | `640x480` |
| `-f`, `--fps`         | Framerate in frames per second (fps).                                                | `15`      |