# 001 - Encoder used for Capturing Video

## Date

2023-01-26

## Status

Decision

## Category

Architecture

## Authors

@roamingthings, @mryel00

## References

[The Picamera2 Library Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

## Context

The Picamera2 library contains different encoders to capture video.

We want to provide an mjpeg video stream and single still images (snapshots).

This software aims at systems that will run additional tasks like 3D printers running Klipper,
Mainsail etc.

## Options

1. Use `JpegEncoder` a multi-threaded software JPEG encoder
2. Use `MJPEGEncoder` an MJPEG encoder using the Raspberry Pi’s hardware

## Decision

We will use the `MJPEGEncoder` that is using the Raspberry Pi's hardware.

## Consequences

* Following the documentation and some experiments this encoder will consume less CPU than the software encoder.
* This encoder is only available on Raspberry Pi hardware

## Useful information

--
