# FloppyToolsExamples

This repo contains some example files for "FloppyTools", to show
how one can salvage individual read errors by hand.

https://github.com/Datamuseum-DK/FloppyTools

You need a big terminal for this example: 140 char by 88 lines

First run:

    python3 -u -m floppytools -F Q1 -d q1

This processes the 35 "readings" of the Q1 floppy disk we use for
the example, enjoy the Unicode graphics :-)

The main Unicode graphic is the cylinders (vertical) and sectors
(horizontal) and their status.

' ' means "non-existent", as in neither read nor defined by the format.

'×' means "Missing", as in defined by the format, but not read.

'╬' means "Conflicting values read"

'ü' (Q1 only) means "conflicting but unallocated".

"░" also indicates conflicts, but one of the values have twice as many readings as the rest combined.

One of '▁▂▃▄▅▆▇█' indicates how many times times that particular sector has a good read.


# Old outdated info

This section needs to be reworked to follow changes that has
happened in FloppyTools. 20250728/phk


By the time the script stops, the last output will be:

    Defects:
        3
        c39h0s18
        c41h0s77
        c7h0s3

After trying to read those three tracks 35 times, I'm pretty sure
more readings will not recover those three sectors, because I actually
read those three tracks 100 times more.

So we have this very unique floppy disk, and are just three sectors
short of a perfect read, what do we do ?

To repair cylinder 7 sector 3, we bruteforce one trouble-some byte:

    python3 -u q1_repair_c7s3.py

Read the comments in the script to understand how that script came to be.

The other two sectors are missing their address marks.  We fix the first one by
running;

    python3 -u q1_repair_missing_am.py

And then remove the comment from these two lines in the script:

    # TARGET = (41, 0, 77)
    # NEIGHBOR = (41, 0, 14)

and run it again, to fix the other one:

    python3 -u q1_repair_missing_am.py

Again: The comments explain who the script came to be.

Now we have a complete image, which you can verify by:

    cat q1/q1.status

And if you're wondering what the heck what is going on with
that floppy:

https://datamuseum.dk/wiki/Q1_Microlite

(If you dont read danish, follow one of the links near the bottom)

/phk
