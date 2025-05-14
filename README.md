# Discord JSON Reader

Discord JSON log parser that exports messages into markdown and generates statistics.
Intended for CS-270 at Drexel University

## Requirements
- Python 3
- Discord channel logs received from Drexel CCI IT

## Files
- `Reader.py`: Main script
- `/Input/`: Directory with logs inside (must be in JSON format)
- `/Output/`: Directory for output (will be created if doesn't already exist)

## Usage
If `Input` directory is in same root directory as `Reader.py`,
`Reader.py` may be ran with no arguments.

## Arguments
- `--input`: Used to specify input directory. If not passed will assume `Input` already exists
in the same directory as `Reader.py`
- `--output`: Used to specify output directory. If not passed will assume `Output` already exists
in the same directory as `Reader.py`
- `--no-stats`: When passed will not produce statistics output for each file

## Errors
- ### "⚠️ No Input directory found, please either specify using \"--input\" or make sure it exists in the CWD"
  - When there is no `Input` directory either inside the directory `Reader.py` was ran from or
  the path given with `--input` does not exist, this error will print to the console and the program will exit
- ### "⚠️ No files found in Input directory"
  - When there are no files inside the `Input` directory.

>**_NOTE:_** Discord allows users to directly reply to previous sent messages in the same channel, and the way I've decided
to format it here is to reference the user and line number that is being replied to, as can be seen in the below example

>**_NOTE:_** Unfortunately due to the nature of Discord's attachment system, file attachments are sent as links and they
expire around 24 hours of being sent, so they are inaccessible. We can see that an attachment was sent and what file type,
but nothing more.

## Output Format Example

---

## MyServerLogs Output
### **general**

1. `2025-05-14 12:13:32` Adam: "This is a message"
2. `2025-05-14 12:15:54` Steve: Replying to @Adam from line `1` - "That is indeed  a message!"

### **pictures**

1. `2025-05-02 18:43:11` Adam: (Attachments: image/jpeg) "Hey @Steve, look at this picture"

---