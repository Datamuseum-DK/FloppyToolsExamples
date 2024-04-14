#!/usr/bin/env python3

'''
   Example repair script for a single stubborn sector
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# This script is an example of how one can read a sector even
# if the address-mark is bad or missing.
#
# The script was built iteratively from top to bottom,
# as the investigation progressed.

import os

from floppytools.main import MediaDir
from floppytools.q1_microlite import Q1MicroLite
from floppytools.kryostream import KryoStream, NotAKryofluxStream
from floppytools.repairtools import Comparator
from floppytools.fluxstream import flux_data

# This is what we're after

MEDIANAME = "q1"
TARGET = (39, 0, 18)
SECTOR_LENGTH = 20

# Explanation below
NEIGHBOR = (39, 0, 80)

# This one also has bad AM
# TARGET = (41, 0, 77)
# NEIGHBOR = (41, 0, 14)

# Open the cached state of this floppy disk
md = MediaDir(MEDIANAME, MEDIANAME, [Q1MicroLite,])

print("# find candidate stream files")
fluxfiles = list(md.stream_files_for(TARGET))

# This is sort of a many-input diff(1) which attempt to show
# where the readings agree and disagree in a useful format
comp = Comparator()

if False:

    # The following fails, because we find no good address-marks

    print("# find flux of candidate sectors")
    for ff in fluxfiles:
        try:
            stream = KryoStream(os.path.join(MEDIANAME, ff))
        except NotAKryofluxStream:
            continue
    
        # Pass a bit more flux than strictly necessary, in case of erasures
        for flux in md.format_class.flux_for_sector(TARGET, stream):
            comp.add_reading(flux[:16*(SECTOR_LENGTH + 10)])
    
    print("# analyze")
    comp.analyze()

# Ok, let's find out what goes on in those tracks...

if True:
    stream = KryoStream(os.path.join(MEDIANAME, fluxfiles[0]))

    for flux_parts in md.format_class.split_stream(stream):
        chs = md.format_class.am_to_chs(stream, flux_parts[0])
        print(chs, " ".join(str(len(x)) for  x in flux_parts[1:]))

# This is part of the output:
#
# (39, 0, 15) 553
# (39, 0, 78) 558
# (39, 0, 16) 561
# (39, 0, 79) 556
# (39, 0, 17) 556
# (39, 0, 80) 748 563
# (39, 0, 81) 555
# (39, 0, 19) 561
# (39, 0, 82) 568
# (39, 0, 20) 563
# (39, 0, 83) 553
#
# From this we can see that
#   A) The sectors are interleaved half a rotation
# and
#   B) our TARGET is missing the address-mark
#
# We process all the fluxfiles and grab the second "data" part after the address mark
# of our new-found NEIGHBOR

found_sectors = {}

for ff in fluxfiles:
    try:
        stream = KryoStream(os.path.join(MEDIANAME, ff))
    except NotAKryofluxStream:
        continue

    for flux_parts in md.format_class.split_stream(stream):

        # Not all AM's might be missing, they could also have bad checksum
        # It's probably safer to work from a good AM, than trying to repair
        # the bad ones, but your mileage may vary.

        if len(flux_parts) < 3:
            continue

        # More than one AM could be missing
        if len(flux_parts[1]) > 800:
            continue

        chs = md.format_class.am_to_chs(stream, flux_parts[0])
        if chs != NEIGHBOR:
            continue

        print(chs, " ".join(str(len(x)) for  x in flux_parts[1:]))
        data = flux_data(flux_parts[2], 1, 2)
        for sect in md.format_class.propose_sector(TARGET, SECTOR_LENGTH, data):
            found_sectors[sect.octets] = sect

print("HITS", len(found_sectors))
assert len(found_sectors) == 1

# Not much to be worried about then...

# Record the hit in the .ft_cache
i = list(found_sectors.values())[0]
i.extra = "repaired"
md.add_sector(i)

# And write the result
md.write_result()
