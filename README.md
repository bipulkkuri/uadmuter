# uadmuter

# POC to mute and unmute youtube ads on TV automatically

## Things needed
* Raspberry Pi or any laptop/macboook server running https://www.home-assistant.io/installation/ follow comprehensive steps available
* A python env to run the python code I used macbook
* Apple iphone to serve as a remote camera ,We utilize the Airplay Continuity
* A TV supporting home-assistant

Enable Apple Airplay & Continutiy Camera on your old phone

List your cameras help functions are list_cameras,get_camera_info

getTextFromImage has all algos/combinations I tried to detect text from images

I am taking 5 sec interval pics to save battery life

```
 python3 -m venv env
 source env/bin/activate
 pip install -r requirements.txt
```

In homeasistant (I am running on raspberry pi) your webhook should be something similar, my samsung tv config 
+Create Automation>Create new Automation>When>Other triggers>Webhook>
I added - GET to keep things simple and since I am inside my local network
```
alias: Samsung TV Un/mute Webhook
description: Samsung TV Un/mute Webhook
triggers:
  - trigger: webhook
    allowed_methods:
      - POST
      - PUT
      - GET
    local_only: true
    webhook_id: "-UDTOb1gERIBVavLHnZVaccnn"
conditions: []
actions:
  - action: media_player.volume_mute
    metadata: {}
    data:
      is_volume_muted: false
    target:
      device_id: 328a3abe5999542ca850961e7b0639fb
mode: single

```

###First Run
```
$python3 uadmuter.py
2025-03-24 16:19:20.532 Python[59078:2811685] WARNING: AVCaptureDeviceTypeExternal is deprecated for Continuity Cameras. Please use AVCaptureDeviceTypeContinuityCamera and add NSCameraUseContinuityCameraDeviceType to your Info.plist.
Text found in the image --  Sponsored
Mute the video 2025-03-24 16:19:51
Text found in the image --  Sponsored
Text found in the image --  Sponsored
UnMute the video 2025-03-24 16:20:13
Text found in the image --  Sponsored
Mute the video 2025-03-24 16:20:20
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
Text found in the image --  Sponsored
UnMute the video 2025-03-24 16:21:21
```

