REM TripleVisualizer.bat
REM Command line 

REM All components visualized, as fast as possible, for 3000 reads, top
REM of screen
start "" python -u FastPM100.py ^
     --controller AllController ^
     --geometry 0,25,1920,333

REM All components visualized, every 10 seconds, for one day, middle of
REM screen
start "" python -u FastPM100.py ^
    --controller AllController ^
    --update 10000 --size 8640 ^
    --geometry 0,385,1920,333

REM All components visualized, every 60 seconds, for 100 days, bottom of
REM screen
start "" python -u FastPM100.py ^
    --controller AllController ^
    --update 60000 --size 144000 ^
    --geometry 0,740,1920,333
