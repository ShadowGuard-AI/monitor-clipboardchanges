![Banner](banner.png)

# monitor-clipboardchanges
Monitors changes to the system clipboard, logging changes to text copied to the clipboard. Can be used to detect potentially malicious copy/paste activity. - Focused on System monitoring and alerts

Only text is captured. For each change after startup, the log records the SHA256 hex digest and the character length of the new text. Clipboard text itself is never written to the log, in clear or in part, so passwords or other text copied for a few seconds are not stored. The text already present on the clipboard at startup is taken as the silent baseline and is not logged. An empty paste result is logged as a cleared or non-text clipboard. If the clipboard cannot be read 5 times in a row, the log states that the clipboard is unreadable and the program exits with status 1. Startup validation failures, such as a non positive interval or a log file directory that does not exist, print an error to stderr and exit with status 1.

## Install
`git clone https://github.com/ShadowStrikeHQ/monitor-clipboardchanges`

## Usage
`./monitor-clipboardchanges [params]`

## Parameters
- `-h`: Show help message and exit
- `--log-file`: Path to the log file.
- `--log-level`: Logging level.
- `--interval`: Interval in seconds to check clipboard changes.

## License
Copyright (c) ShadowStrikeHQ
