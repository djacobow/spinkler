
# SPinkler 

The SPinkler is a Raspberry Pi based sprinkler controller. There are others
like it, but this one is mine.

## Hardware

The hardware for the SPinkler is not a whole lot different fromt he Open
Sprinkler project. Then again, just about any IoT sprinkler system is 
going to look similar.

This implementatino assumes a 24VAC transformer as a power supply, which
feeds into a simple switching regulator to provide 5V power for a 
Raspberry Pi Zero W, which is mounted on a SIP sockect on the board. 
Most Raspberry Pi's will have their pins sticking up on the component
side of the board, but for this application it makes sense to put the pins
on the back.

The Pi then provides serial data clocked into one of two 74HC595 shift
registers. One of those shift registers drives a 16x2 LCD and the other
drives a set of 8 triacs.

That and some connectors and fuses are all she wrote. I decided to use 
automotive ATO style fuses, and there are separate ones for the power 
supply and logic and for the sprinkler heads themselves.

## Software

Lots of sprinkler projects do clever stuff like adjust to the weather,
either by Internet or by rain sensor. I decided to eschew all this by
just creating a simple Python-based API to control the sprinklers directly,
along with an example program that works from a Google Calendar.

The nice thing about using Google Calendar is that I do not need a 
special phone app, and can set up any kind of arbitrary repeating 
calendar event I like, and I can do it from any device without installing
any software. Google, of course, will know your sprinkler schedule,
but nobody else will. This is IoT how I like it -- no middle men 
collecting my data.

## Setup

### Hardware

Setup is pretty simple. Hardware-wise, just plug in a 16x2 LCD to 
the SIP for the LCD and plug in a Raspberry Pi Zero into the SIP for
the controller.

### Software

1. Install an OS on your Raspberry Pi Zero. I like Raspbian Lite because
   I won't be using the gui and why bring in more software than you need?

2. Install Python3 if it is not already on there:

```sh
sudo apt install python3
```

Also, install a few packages. You can do some of these with pip, but I prefer
to get them from the apt repos when I can.

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

    1. Go to console.cloud.google.com and creata project by clicking on the 
down triangle at the top and then clicking "new project"
    2. name the project and fill in whatever you want or not, it doesn't really matter
    3. Click on API's and services, search for Calendar API and click to enable that
    4. generate credentials. You can use the help walkthrough to figure out what you will need, but basically you want a client_id. Tell it that you will be accessing user data from a CLI UI.
    5. download the credential you just made and save it in the folder your
just created with your git pull as `spinkler_client_secrets.json`.

This credential does not give access to your Google Account. It identifies the 
app and lets the app *request* credentials to see your Google Account account.

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
notice it only asks for your login once. After that, it will remember.

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

just run 

`
./spinkler.py
`

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


