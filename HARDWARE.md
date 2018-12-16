## Hardware Description

The hardware for the SPinkler is not very from the
Open Sprinkler Project or really any triac sprinkler board for that
matter. The difference here is really form factor and an LCD display.

Only a few GPIO pins on the RPi are used. They drive one or two 74HC595 
shift register to control 8 or 16 triacs, and another 595 drives
the LCD display.

The board is intended to mate with a Raspberry Pi Zero W. 

## Hardware Setup

### Connect the Pi

This board was intended to have a Pi Zero W ride on top of 
the board. This is sort of like a "hat" but backwards, since 
this board is so much larger than a Pi, it didn't make sense to 
have it on top of the Pi.

I found it most convenient to solder a socket onto the SPinkler
board and the header pins onto the underside of the Pi Zero W
board. This way, the Pi Zero just "plugs into" the SPinkler. It's
very neat and robust.

However, regular Pi users may find this arrangement a little 
uncommon. Most Pi's have their headers on top. If yours is like
this, and you don't want to change it, you can still attach your
Pi Zero (or any Pi for that matter) to the SPinkler board by means
of an IDC cable.

In this case, you will want to solder header pins onto the
SPinkler. Then, use a double-female 40 pins IDC cable to mate
them. Physically mounting the Pi will be a bit awkward, but
with standoffs, it should be possible to work something out.
If using a regular sized Pi (not a zero), you may need a larger
box.

### LCD

This board will accomodate a 16x2 or 20x4 standard Hitach
HD44780 LCD. The software expectes the 20x4. You may need to 
solder a 16x1 header onto the LCD if it does not already have
one. Then you just plug it int. Holes on the SPinkler will 
match holes on the LCD. You can use m2.5 size standoff hardware
to secure everything.

### Power

Power for this board should come from a 24Vac plug-pack. This is 
likely what powered your old sprinkler controller, so you can just
re-use that one. If you don't have one, you can get a generic 1A
24 Vac plug pack on Digikey or Mouser.

If your plug-pack has a connector on the end, cut it off and 
separate the wires. Twise the ends, and put them into `AC_IN_1`
and `AC_IN_0` terminal at teh bottom of the left screw terminal
block.

### Srprinklers

Each sprinkler valve will have two wires. One wire goes into 
a scew terminal for a zone, on the board marked "Z1", "Z2", etc.
The other wires are "common" and can all go together into the
"common" terminal at the bottom of the scew terminal block. For
convenient, two holes for common on each side of the board are
provided, though they are all the same electrically.

with the pins facing towards the back of the board. This is not
generally how most people put header pins on a Pi, and it is not
the way a pre-soldered Pi will come.

So, if you want to use this board, you have 
The Pi Zero attached via a 2x20 header. I put the socket on the
SPinkler board and solder header pins to the *back* of a RPi Zero.
You could do it the other way around, I suppose.

Like almost all sprinklers, a 24VAC transformer provides power.
5V comes from the venerable MC34061 switching regulator, which feeds 
The Pi Zero by means of the GPIO socket.

A simple driver for a 20x4 LCD display allows HD44780 commands over
the serial line.

That and some connectors and a fuse are pretty much all she wrote. 
I decided to use automotive ATO style fuse bcause I prefer them
over bus types. They're easier to pull and read.

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

