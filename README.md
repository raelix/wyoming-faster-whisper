# wyoming-mlx-whisper

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) speech to text system, forked from [wyoming-faster-whisper](https://github.com/rhasspy/wyoming-faster-whisper).

## Home Assistant Add-on

[![Show add-on](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_whisper)

[Source](https://github.com/home-assistant/addons/tree/master/whisper)

## Local Install

Install ffmpeg:

``` sh
# on macOS using Homebrew (https://brew.sh/)
brew install ffmpeg
```

Clone the repository and set up Python virtual environment:

``` sh
git clone https://github.com/raelix/wyoming-faster-whisper.git
cd wyoming-faster-whisper
script/setup
```

Run a server anyone can connect to:

```sh
./script/run --model "mlx-community/whisper-large-v3-mlx" --language en --uri 'tcp://0.0.0.0:10300'
```

The `--model` can also be a HuggingFace model like `mlx-community/whisper-medium.en-mlx` or `mlx-community/whisper-large-v3-turbo`

## Docker Image

``` sh
docker run -it -p 10300:10300 -v /path/to/local/data:/data rhasspy/wyoming-whisper \
    --model tiny-int8 --language en
```

[Source](https://github.com/rhasspy/wyoming-addons/tree/master/whisper)


## launchctl service

To keep this running, directly on MacOS, also after reboots, etc., you could for example create a file in ~/Library/LaunchAgents/ , paste this inside (but change the `/full/path/to/project/folder`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.whisper.service</string>

    <key>WorkingDirectory</key>
    <string>/full/path/to/project/folder</string>

    <key>ProgramArguments</key>
    <array>
        <string>./script/run</string>
        <string>--model</string>
        <string>mlx-community/whisper-large-v3-turbo</string>
        <string>--language</string>
        <string>de</string>
        <string>--uri</string>
        <string>tcp://0.0.0.0:10300</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardErrorPath</key>
    <string>/tmp/com.user.whisper.service.err</string>

    <key>StandardOutPath</key>
    <string>/tmp/com.user.whisper.service.out</string>

</dict>
</plist>
```

Load and run and keep running via

```sh
launchctl load ~/Library/LaunchAgents/com.user.whisper.service.plist
```

Check logs via for example

```sh
cat /tmp/com.user.whisper.service.err  
```
