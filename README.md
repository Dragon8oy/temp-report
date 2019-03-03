# temp-report
A small project to report the temperature of a room to anyone on the mailing list when it reaches a certain temperature with an integrated csv editor

## Dependencies:

* Python 3.6+
* Tmux

## Commands and notes

- Install with `git clone https://github.com/Dragon8oy/temp-report.git` and `sudo pip3 install w1thermsensor`
- Make sure OneWire is enabled
- Add `tmux new-session -d -s temp_report 'python3.6 /path/to/install/temp.py; exec bash -i'` to `crontab -e` to have the program start on boot
- Use `tmux att -t temp_report` to view the program
- Use `python3.6 temp.py -h` to view help

## Wiring diagram:


