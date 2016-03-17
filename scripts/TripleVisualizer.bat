REM TripleVisualizer.bat
REM Command line 

REM All components visualized, as fast as possible, for 3000 reads, top
REM of screen
call "python -u FastPM100.py ^
     --controller AllController ^
     --geometry 0,0,1920,333"

REM All components visualized, every 10 seconds, for one day, middle of
REM screen
call "python -u FastPM100.py ^
    --controller AllController ^
    --update 10000 --size 8640 ^
    --geometry 0,333,1920,333"

REM All components visualized, every 60 seconds, for 100 days, bottom of
REM screen
call "python -u FastPM100.py ^
    --controller AllController ^
    --update 60000 --size 144000 ^
    --geometry 0,667,1920,333"
