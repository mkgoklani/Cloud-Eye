#!/bin/sh
# Auto-generated recording loop
# This script will be run by the 'recorder' container

# Wait for Go2RTC to start
echo "Waiting 10s for Go2RTC..."
sleep 10

mkdir -p /storage/Demo_Bunny_1_1_1_1
ffmpeg -nostdin -re -i rtsp://go2rtc:8554/Demo_Bunny_1_1_1_1 -c copy -f segment -segment_time 900 -strftime 1 /storage/Demo_Bunny_1_1_1_1/%Y-%m-%d_%H-%M-%S.mp4 &

mkdir -p /storage/Demo_Sintel_2_2_2_2
ffmpeg -nostdin -re -i rtsp://go2rtc:8554/Demo_Sintel_2_2_2_2 -c copy -f segment -segment_time 900 -strftime 1 /storage/Demo_Sintel_2_2_2_2/%Y-%m-%d_%H-%M-%S.mp4 &

mkdir -p /storage/Demo_Tears_3_3_3_3
ffmpeg -nostdin -re -i rtsp://go2rtc:8554/Demo_Tears_3_3_3_3 -c copy -f segment -segment_time 900 -strftime 1 /storage/Demo_Tears_3_3_3_3/%Y-%m-%d_%H-%M-%S.mp4 &

wait
