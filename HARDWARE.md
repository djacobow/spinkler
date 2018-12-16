## Hardware Description

The hardware for the SPinkler is not very different from the
Open Sprinkler Project or really any triac sprinkler board for that
matter. The difference here is really form factor and an LCD display.

Only a few GPIO pins on the RPi are used. They drive one or two 74HC595 
shift register to control 8 or 16 triacs, and another 595 drives
the LCD display.

The board is intended to mate with a Raspberry Pi Zero W but using
an IDC cable you can connect it to any RPi, even the ones with only
10x2 headers. (only pins in the first 10 columns are used).

The following is a picture of the board without the Pi or LCD attached.
This particular board is only fitted for 8 zones, but can be exanded
to sixteen. (Also, as you can see, this pre-production board has a 
minor bodge that has already been corrected for the next version.)

![picture of Complete SPinkler without LCD and Pi](https://raw.githubusercontent.com/djacobow/spinkler/master/hardware/images/complete_8ch.jpg)

When everything is plugged in, it looks like this:

![Operating, assembled SPinkler](https://raw.githubusercontent.com/djacobow/spinkler/master/hardware/images/complete_operating.jpg)
## Obtaining the Hardware

This board will be available soon on Tindie in both 8-zone and
16-zone versions. I am still finalizing a production run and pricing.

If you are impatient, th schematics for this hardware are available
in this github repo, but I will not be providing gerbers here.  If you
would like to fab this design yourself, contact me and I will send you
the appropriate gerbers under the promise that you will not distribute
them or use them for commercial purposes.

## Hardware Setup

### Connect the Pi

This board was intended to have a Pi Zero W ride on top. This is 
the reverse of the normal "hat" setup where a board attached to 
a Pi. Because this board is so much larger than a Pi Zero, that 
would have been awkward.

Therefore, I found it most convenient to solder a socket onto the
SPinkler board and the header pins onto the underside of the Pi Zero W
board. This way, the Pi Zero just "plugs into" the SPinkler. It's 
simple and robust.

![Expected mounting of Pi Zero W](https://raw.githubusercontent.com/djacobow/spinkler/master/hardware/images/pi_zero_mounted.jpg)

However, regular Pi users may find this arrangement strange.
Pi's have their headers on top. If yours is like
this, and you don't want to move the header, you can still attach your
Pi to the SPinkler board by means of an IDC cable.

![Alternative Connection of Another RPi](https://raw.githubusercontent.com/djacobow/spinkler/master/hardware/images/rpi3_connected.jpg)

In this case, you will want to solder header pins onto the
SPinkler instead of a socket. The IDC cable does not need to be 
a full 40-pin cable for the entire RPi header. A 20-pin
cable and a ten-row connector are adequate. However, if you use
a narrower cable, you may have trouble plugging it into the Pi
because the extra pins interfere with the edge of the connector.

Physically mounting the Pi may be a bit awkward, but with mounting holes
and standoff hardware, it is possible.

### LCD

This board will accommodate a 16x2 or 20x4 standard Hitachi 
HD44780 LCD. The software expectes to see 20x4, but you can
change it for 16x2. You may need to solder a 16x1 header 
onto the LCD if it does not already have one. Then you just 
plug it in. Holes on the SPinkler will match holes on the 
LCD. You can use m2.5 size standoff hardware to secure everything.

### Power

Power for this board should come from a 24Vac plug-pack. This is 
likely what powered your old sprinkler controller, so you can just
re-use that one. If you don't have one, you can get a generic 1A
24 Vac plug pack on Digikey or Mouser.

!!! DO NOT ATTACH THIS BOARD TO 120V MAINS POWER !!!

If your plug pack has a connector of any kind on the end, 
cut it off and separate the wires. Twise the ends, and put them 
into `AC_IN_1` and `AC_IN_0` terminal at the bottom of the 
left screw terminal block.

Make sure there is a fuse in the fuse holder. A 2A ATO "auto"
fuse is appropriate.

### Sprinklers

Each sprinkler valve will have two wires. One wire goes into a scew
terminal for a zone, on the board marked "Z1", "Z2", etc.  The other
wires are "common" and can all go together into a "common" terminal
at the bottom of the scew terminal block. For convenience, two 
holes commons on each side of the boaard are provided. They are all
electrically connected.


## Case

The holes on the SPinkler board will match those found on the 
inside of a Hammond RP-1285 box. You can use this box, which 
comes in a few different materials, with an opaque or see-through
cover, or you can mount the board directly onto your garage 
wall or whatever. There is nothing "unsafe" about the board,
so it doesn't really need to be in a box.

If you do buy a Hammond RP-1285 or similar, of course you
will need to dril some holes for wires.

If you use another box, do not choose metal. Remember, you 
have a computer with WiFi inside there.

