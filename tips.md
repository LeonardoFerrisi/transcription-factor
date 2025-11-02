# Some random tips

## If downloading videos from CANVAS

+ Inspect Element
+ Network Inspect
+ Start playing a video and pause the network inspect.
+ Video is some GET request starting with    `https://cfvod.kaltura.com` 
+ This link will have some segment that says `scf/hls`. This indicates it's an HLS stream.
    + Replace `scf/hls` with `pd` to get the full video file link.
+ Paste that link into another empty tab and you can download it directly.