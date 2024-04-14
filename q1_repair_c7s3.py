#!/usr/bin/env python3

'''
   Example repair script for a single stubborn sector
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# This script is an example of how one can attempt to
# recover a single stubborn sector, given so many
# readings that a pattern can be discerned.
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
TARGET = (7, 0, 3)
SECTOR_LENGTH = 255

# Open the cached state of this floppy disk
md = MediaDir(MEDIANAME, MEDIANAME, [Q1MicroLite,])

print("# find candidate stream files")
fluxfiles = list(md.stream_files_for(TARGET))

# This is sort of a many-input diff(1) which attempt to show
# where the readings agree and disagree in a useful format
comp = Comparator()

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

# The output looks like this:
#
# R  0   49 [677] [613] [932] [478] -|-|--|--|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|
# R  1   39 [677] [613] [932] [478] -|-|--|--|--|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-
# R  2   15 [677] [613] [932] [478] -|-|--|--|-|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-
# R  3   13 [677] [613] [932] [478] -|-|--|--|---|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|
# R  4   12 [677] [613] [932] [478] -|-|---|-|---|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|
# R  5    8 [677] [613] [932] [478] -|-|---|--|--|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|
# R  6    7 [677] [613] [932] [478] -|-|---|--|---|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-
# R  7    4 [677] [613] [932] [478] -|-|---|-|--|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-
# R  8    3 [677] [613] [932] [478] -|-|---|-|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] --- [104] |-|-
# R  9    2 [677] [613] [932] [478] -|-|---|-|-|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-
# R 10    1 [677] - [613] - [932] - [478] --|-|--|-|-|-|-|-| [309] -|--|---|-|- [36] [62] -| [28] -|---|--|- [475] - [480] [104]
# R 11    1 [677] [613] [932] [478] -|-|---|--|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] --- [104] |-|
# R 12    1 [677] [613] [932] [478] -|-|---|--|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-
# R 13    1 [677] [613] [932] [478] -|-|---|-|--|-|-|-|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|
# R 14    1 [677] [613] [932] [478] -|-|--|--|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] --- [104] |-|-
# R 15    1 [677] [613] [932] [478] -|-|--|-|---|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-
# R 16    1 [677] [613] [932] [478] -|-|--|-|--|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|-|-|
# R 17    1 [677] [613] [932] [478] -|-|-|-|-|--|--|--|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] [104] |-|-|
# R 18    1 [677] [613] [932] [478] |-|---|--|--|---|- [309] |--|---|-| [36] - [62] |- [28] |---|--| [475] [480] --- [104] |-|-
#
# The first column is an index, we'll use this in a moment
# The second column is how many readings had this flux pattern
# In the summarized flux pattern '[%d]' means "a common flux this long"
#
# Looking at the above, index 10 is clearly "out of family", so we drop it.

comp.readings.pop(10)

# And reanalyze

print("# reanalyze")
comp.analyze()

# Now we get:
#
# R  0   49 [2700] -|-|--|--|--|-- [1414] | [108] -|
# R  1   39 [2700] -|-|--|--|--|- [1414] | [108] -|-
# R  2   15 [2700] -|-|--|--|-|-- [1414] | [108] -|-
# R  3   13 [2700] -|-|--|--|---|- [1414] | [108] -|
# R  4   12 [2700] -|-|---|-|---|- [1414] | [108] -|
# R  5    8 [2700] -|-|---|--|--|- [1414] | [108] -|
# R  6    7 [2700] -|-|---|--|---|- [1414] | [108] -
# R  7    4 [2700] -|-|---|-|--|- [1414] | [108] -|-
# R  8    3 [2700] -|-|---|-|--|-- [1414] -- [108] -
# R  9    2 [2700] -|-|---|-|-|-- [1414] | [108] -|-
# R 10    1 [2700] -|-|---|--|--|-- [1414] -- [108]
# R 11    1 [2700] -|-|---|--|--|-- [1414] | [108] -
# R 12    1 [2700] -|-|---|-|--|-|-| [1414] | [108]
# R 13    1 [2700] -|-|--|--|--|-- [1414] -- [108] -
# R 14    1 [2700] -|-|--|-|---|- [1414] | [108] -|-
# R 15    1 [2700] -|-|--|-|--|- [1414] | [108] -|-|
# R 16    1 [2700] -|-|-|-|-|--|--|- [1414] | [108]
# R 17    1 [2700] |-|---|--|--|-- [1414] -- [108] -
#
# Much better!
#
# It seems obvious that there is one particular troublesome region.
# The Q1 always writes 0x10 after the checksum byte, and some
# testing not included here told us that the trouble region must
# be 14 long for that to happen.
#
# We need (SECTOR_LENGTH+2)*16 = 4112 which is less than
# 2700+14+1414 = 4128 so we can brute force a 14 bit segment
# sandwiched between the [2700] and [1414] sequences
#
# Trying that we got no hits with good checksum, so in
# second round we brute-forced ±1 on either side (= 16 bits)

hole = 16
hits = {}
for i in range(1<<hole):
    flux = []

    # the good prefix
    flux.append(comp.readings[0][0].flux[:-1])

    # our brute-force attempt
    j = bin((1<<hole)|i)[3:]
    fill = j.replace('0', '-').replace('1', '|')
    flux.append(fill)

    # the good suffix
    flux.append(comp.readings[0][2].flux[1:])

    flux = ''.join(flux)[:(SECTOR_LENGTH + 2) * 16]
    data = flux_data(flux, 1, 2)

    # Ask the format if this guess is any good
    # (We expect 256 hits, because the clock bits are ignored)
    for j in md.format_class.propose_sector(TARGET, SECTOR_LENGTH, data):
        hits[j.octets] = j

# As expected we get only a single actual hit, because a 16 wide
# segment only touches 8 data bits, and even the Q1 format's single-byte
# checksum will only allow one of those through.

print("HITS", len(hits))
assert len(hits) == 1

# Record the hit in the .ft_cache
i = list(hits.values())[0]
i.extra = "repaired"
md.add_sector(i)

# And write the result
md.write_result()
