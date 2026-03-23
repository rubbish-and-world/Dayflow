## Run as service and start at login

```bash
vim ~/Library/LaunchAgents/com.tinnodjtk.godiswatching.plist
```


```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tinnodjtk.godiswatching</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/tinnodjtk/Desktop/GodisWatching/.venv/bin/python</string>
        <string>/Users/tinnodjtk/Desktop/GodisWatching/main.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/tinnodjtk/Desktop/GodisWatching/monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/tinnodjtk/Desktop/GodisWatching/monitor_error.log</string>
</dict>
</plist>
```


## Enable monitoring

```bash
launchctl load ~/Library/LaunchAgents/com.tinnodjtk.godiswatching.plist
```

## Disable monitoring

```bash
launchctl unload ~/Library/LaunchAgents/com.tinnodjtk.godiswatching.plist
```