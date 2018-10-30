
# SPinkler 

The "SPinkler" is a Raspberry Pi based sprinkler controller. There are others
like it, but this one is mine. The name is a mashup of "sprinkler" and "pi."

## Hardware

The hardware for the SPinkler is not much different from the Open
Sprinkler project. Then again, just about any IoT sprinkler system is 
going to look very similar.

In my case, I wanted the design to work with a Pi Zero attached by the
DIP header. The header is on the Spinkler board, and the pins are on the
*back* of a Raspberry Pi Zero. The Pi sends commands to the board by
shifting bits into one of two 74HC595 shifter register on the board. One
drives the LCD display, the other drives an array of triacs.

Like almost all sprinklers, a 24VAC transformer provides power.
5V comes from the venerable MC34061 switching regulator, which feeds 
The Pi Zero by means of the GPIO socket.

The Pi then provides serial data clocked into one of two 74HC595 shift
registers. One of those shift registers drives a 16x2 LCD and the other
drives a set of 8 triacs.

A simple driver for a 16x2 LCD display allows HD44780 commands over
the serial line.

That and some connectors and fuses are pretty much all she wrote. 
I decided to use automotive ATO style fuses, and there are separate 
ones for the power supply and logic and for the sprinkler heads 
themselves.

## Software

### Philosophy

Lots of sprinkler projects do clever stuff like adjust to the weather,
either by Internet feed or by rain sensor. Most include a phone app
to allow real-time control of your sprinklers.

I decided to eschew all that and keep things very simple, though of 
course you can build whatever you want on top of this.

What I have done is build a simple scheduler that pulls its data
from Google Calendar. You create a special calendar in your Google 
Account and give the Spinkler access. It then waters according to
events on that calendar.

The nice thing about using Google Calendar is that I do not need a 
special phone app, and can set up any kind of arbitrary repeating 
calendar event I like, and I can do it from any device without installing
any software. Google, of course, will know your sprinkler schedule,
but nobody else will. This is IoT how I like it -- no middle men 
collecting my data.

### Libraries

I really tried hard to keep this very simple, so that there is nothing
too clever in the Python code, and the bare minimum external libraries
are used.

I provide simple libraries to:

    * write to the display
    * turn on triacs
    * read from Google Calendar

The main app just uses those to run a schedule.

You can use as little or as much of this as you like, and I'll be 
happy to take pull requests.



## Getting Started

### Hardware Setup

1. obtain a 16x2 LCD and solder a 16-pin 0.1" header to the 
   back of it so that the pins point backwards

2. obtain the 20x2 0.1" header for a Raspberry Pi Zero W
   and solder those pins on, also on the back

3. Attach the LCD and Pi Zero the main board. You can use
   mounting hardware to secure them. The holes should line up

4. insert fuses into the fuse holder. 1A for the left and 2A 
   for the right would be ideal

5. Get a 24 VAC plug pack (perhaps from your old controller) and
   attach the wires to the 24VAC AC1 and AC0 terminals of the board

### Software Setup

1. Install an OS on your Raspberry Pi Zero. I like Raspbian Lite because
   I won't be using the gui and why bring in more software than you need?

2. Install Python3 if it is not already on there:

   ```sh
   sudo apt install python3
   ```

   Also, install a few packages. You can do some of these with pip,
   but I prefer to get them from the apt repos when I can.

   ```sh
   sudo apt install \
       python3-rpi.gpio \
       python3-dateutil \
       python3-googleapiclient
   ```

    3. Create a working directory for this project and clone the code to it:

       ```sh
       cd ~
       git clone https://github.com/djacobow/spinkler
       cd spinkler
       ```

    3. Create a Google Project

       The code to run the calendar is going to run under a Google Project
       that *you* control rather than me. You will need to create a project,
       turn on the Calendar API, generate a credential, and download it.

       Without getting too much into how this all works, these are the
       basic steps:

       * Go to console.cloud.google.com and creata project by clicking on the 
         down triangle at the top and then clicking "new project"
       * name the project and fill in whatever you want or not, it doesn't 
         really matter
       * Click on API's and services, search for Calendar API and click to 
         enable it. 
       * generate credentials. You can use the help walkthrough to figure out 
         what you will need, but basically you want a client_id. Tell it that 
         you will be accessing user data from a CLI UI.
       * download the credential you just made and save it in the folder your
         just created with your git pull as `spinkler_client_secrets.json`.

       This credential does not give access to your Google Account. It 
       identifies the app and lets the app *request* credentials to see your 
       Google Account account.

    4. Run the script `list_cals.py`

       When you do, you will be presented with an URL. Copy and paste this to your
       browser, log in, and then copy and paste the resulting token back into
       your text window.

       Once you have done that, `list_cals.py` will show a list of calendars that
       your account can see. You can use one of these for your sprinklers, but 
       I suggest instead you creat a calendar just for the purpose.

       Open Google Calendar in a browser, and click the plus sign next to "Add
       a friend's calendar", then click "New Calendar" and give it a name, etc.

       If you've created a new calendar, run the list_cals script again. You'll
       notice it only asks for your login once. After that, it will remember by
       storing a token in `~/.spinkler`.

       Anyway, copy the calendar ID associated with the calendar you want to use
       and paste it into spinkler.py in the config section under the key
       `"sprinkler_calendar"`.

    5. Create your sprinkling schdule

    It's easy to add a watering to your schedule. Just create an event
    in the calendar the Spinkler can see (the one you just edited into
    Spinkler.py) and set the title to "water". The description tells 
    what zones you want watered and how long, in this format:


    ```
    run 3 duration 2
    run 4 duration 0.2
    run 5 duration 0:02
    ```

    In this case, zones 3, 4, and 5 will be run sequenually for 2 hours,
    0.2 hours (that's 12 minutes) and 2 minutes, respectively. As you see,
    each lien starts with "run" then the zone number to run, then the 
    duration to run in either hours (fractions allowed) or hours:minutes

    You can create as many events as you like, they can repeat, run only on 
    weekdays, etc, whatever you want.

    6. Run the spinkler program:

    Just run:

    ```
    ./spinkler.py
    ```

    and you should be off to the races.

    You can run it now to see if it works. Once you have it working 
    properly, you can set it up to run as a service so that it starts
    automatically at boot and will be restarted automatically if it crashes for
    some reasons

    ```sh
    cp spinkler.service /etc/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable spinkler
    sudo systemclt restart spinkler
    ```

    You can see how spinkler is doing with:

    ```
    sudo journalctl -f -u spinkler
    ```



That's about all there is to it. Good luck!

#### Author

Dave J (djacobow)

#### Date

Started October 2018


