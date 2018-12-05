
# SPinkler 

The "SPinkler" is a Raspberry Pi based sprinkler controller. There are others
like it, but this one is mine. The name is a mashup of "sprinkler" and "pi."

## Hardware

The hardware for the SPinkler is not a whole lot different from the
Open Sprinkler Project or really any triac sprinkler board for that
matter. The difference here is really form factor and an LCD display.

Only a few GPIO pins on the RPi are used. They drive an 74HC595 shift
register to control the triacs and another 595 to drive the LCD display.

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

## Software

### Philosophy

Lots of sprinkler projects do clever stuff like adjust to the weather,
either by Internet feed or by rain sensor. Most include a phone app
to allow real-time control of your sprinklers.

I might get around to some or all of that, but the main feature I 
wanted to implement was setting your watering schedule by means of 
a Google Calendar. Google allows an individual accout to have
multiple calendars, so I just created one for my watering. This
Pi then just reads that schedule and waters accordingly. This is
clean and simple and allows me to edit my watering using any of 
the interfaces to Google Calendar (phone, web, etc) without having
to write (or use) a special app.

Google, of course, will know your sprinkler schedule, but nobody 
else will. This is IoT how I like it -- no middle men collecting 
my data.

I have not done anything yet regarding adjusting to weather, but 
I have started to pull in local METAR data from the nearby airport.
In theory, I could incorporate this into whether or not to carry
out the pre-programmed schedule normally.


### Libraries

I really tried hard to keep this very simple, so that there is nothing
too clever in the Python code, and the bare minimum external libraries
are used.

I provide simple libraries to:

    * write to the display
    * turn on triacs
    * read from Google Calendar

The main app just uses those to run a schedule.

The main app also runs a simple web server, which you can use 
to set up your Google credentials and adjust a few other basic
parameters.

You can use as little or as much of this as you like, and I'll be 
happy to take pull requests.



## Getting Started

### Hardware Setup

1. obtain a 20x4 LCD and solder a 16-pin 0.1" header to the 
   back of it so that the pins point backwards

2. obtain the 20x2 0.1" header for a Raspberry Pi Zero W
   and solder those pins on, also on the back

3. Attach the LCD and Pi Zero the main board. You can use
   mounting hardware to secure them. The holes should line up

4. insert a fuse into the fuse holder. 1A or 2A should be fine

5. Get a 24 VAC plug pack (perhaps from your old controller) and
   attach the wires to the 24VAC AC1 and AC0 terminals of the board



### Software Setup

This assumes basic familiarity with the Raspberry Pi.

1. Install an OS on your Raspberry Pi Zero.

   I like Raspbian Lite because it brings in no gui or other
   cruft which is not helpful for this project and just increases
   the size of the install and of updates.

   While setting it up, you will probably find it convenient to 
   power it up on its own (not on the SPinkler board) with a monitor
   and keyboard attached. I usually do this long enough to enable 
   ssh and set the WiFi password, and then from there on out I 
   connect to it from another computer via ssh.

2. Some prelimiary setup:

   * change your password

   * use `raspi-config` to enable ssh so you can log in remotely

   * set your WiFi credentials (`/etc/wpa_supplicant/wpa_suplicant.conf`)
  
   * name the machine something like "spinkler.local" so that 
     avahi/mDNS can broadcast a real name. This is important, as 
     Google with not auth against an IP address
 
3. Install Python3 if it is not already on there:

   ```sh
   sudo apt install python3
   ```

   Also, install a few packages. You can get these from pip3 but I
   prefer to get the OS packages when they exist. That way they
   get picked up with OS updates.

   ```sh
   sudo apt install \
       python3-rpi.gpio \
       python3-dateutil \
       python3-googleapiclient \
       python3-oauth2client \
       python3-flask \
       python3-gunicorn \
       python3-xmltodict
   ```

4. Create a working directory for this project and clone the code to it:

   ```sh
   cd ~
   git clone https://github.com/djacobow/spinkler
   cd spinkler
   ```

5. Create a Google Project

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
   * generate credentials. Google's credentials system is pretty
     confusing, and they do not make it easy to host a web server
     locally on a private network and use Google services.

     You will have to specify your machine name (spinkler.local)
     or whatever you have named is in a few places:

         - on the oauth consent screen tab, add some 
           public website as an authorized domain. You won't be
           logging in from this domain, but Google insists on 
           being able to redirect you to somehwere afer login,
           and that somehwere needs to be a public address

     Then, under the credentials tab, edit the credential for
     your web app and:
 
         - under "authorized Javascript origins", add:
           `localhost:5000` and 
           `spinkler.local:5000`

         - under "authorized redirect URIs."
           This must be a complete url in the site you 
           listed above. It can literally be any page.


   * download the credential you just made and save it in the folder your
     just created with your git pull as `web_client_secrets.json`.

   This credential does not give access to your Google Account. It 
   identifies the app and lets the app *request* credentials to see your 
   Google Account account.

6. If you have not yet created a Google Calendar for your SPinkler, do
   so now.  Open Google Calendar in a browser, and click the plus sign 
   next to "Add a friend's calendar", then click "New Calendar" 
   and give it a name, etc.

7. If you are still ssh'd into your Pi, get the IP address using 
   `ifconfig`. 


8. Start the program server:

   `gunicorn -b 0.0.0.0:5000 --pid=app.pid web_spinkler:spinkler_app`

9.  If it starts without errors, use your browser to open
    `http://<ip_address>/login`.

   Click 'login' to log into your Google account. Grant the requested
   permissions.

   If you log in successfully, you will be taken to a configuration
   screen where you can choose what calendar the tool should use.

   If you've created a new calendar, run the list_cals script again. You'll
   notice it only asks for your login once. After that, it will remember by
   storing a token in `~/.spinkler`.

10. Create your sprinkling schdule

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
weekdays, etc, whatever you want. You can put more than one zone 
in a Calendar event, or you can make a separate Calendar event for 
each zone you'd like to run.

11. Make the spinkler program a daemon.

If the spinkler program appear to be running/working, convert it
into a background process that will auto-restart if something fails.
First, use ctrl-c to exit the instance you have running.

Then, issue these commands to "daemonize" your program:

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

Updated December 2018
Started October 2018


