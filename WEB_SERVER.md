
# SPinkler web server

The main software code for the SPinkler project is reasonably simple. A
python script checks Google Calendar and controls the valves/triacs
based on a schedule.

The script itself is most easily configured simply by ssh-ing into the
host Pi and editing a JSON file. This is described in the `README.md`
file.

However, what would be even more convenient for most users would be if 
they could configure or adjust the SPinkler software from a web page
that the host Pi serves. Well, that's convenient to use, but it's a 
bit more effort to set up.

This document the experimental version of a web server with 
configuration. It uses most of the same files and adds 
a web server layer.


## Google Authentication

Google has various authentication methods for different kinds of 
apps: apps that a user accesses from a server, apps that run from a 
phone, apps that run from a comand line, etc. They do not seem to 
have an authentication method for apps that run from a server, that
act on behalf of a user and which cannot be accessed from the Internet
at large. (That is, Google's servers themselves cannot access your
server.)

This is somewhat a problem for running a little home-based server
that uses Google services. But we can work around it.


## Setup

### Basic Setup for the Pi

First, get the `noweb_spinkler.py` working as described in the main
`README.md`. There is no sense futzing with the extra complexity of 
the web server if you don't have the rest already working. 

In addition to what's there:

1. name the machine using rasp-config.
   Something like "spinkler.local" so that avahi/mDNS can broadcast 
   a real name. This is important, as Google with not auth against 
   an IP address. On your local network you'll be able to access
   that machine by going to http://spinkler.local, for example.

2. Install some additional libraries:

   ```sh 
   sudo apt install \
       python3-flask \
       python3-gunicorn \
       python3-xmltodict
   ```

In Raspbian, I have found that gunicorn does not install
properly from apt, so you may want to use pip3 instead.
For that matter, you might want to use virtualenv.


### Generate Google Credentials for a "Web App"


If you set up the software according to the instructions in
`README.md`, you already have a Google Project with Calendar
API and Gmail API enabled. In that process, you created 
a "client secret" file and called it `console_client_secret.json`

Now we will generate a new credential for the web server.

Go to your cloud project and go to make new credentials, except
this time, tell Google that you are making a "web app".

You will have to specify your machine name (I'll assume 
"spinkler.local" here) or whatever you have named is in a few 
places:

Under the credentials tab, edit the credential for your web 
app and:
 
* under "authorized Javascript origins", add:
  `localhost:5000` and 
  `spinkler.local:5000`

* under "authorized redirect URIs." provide a 
  URI to some web page.

  This is a bit confusing. Because your SPinkler
  is almost certainly operating behind a NAT 
  firewall, Google cannot access this webserver,
  only you can at home. As a result, you will not
  be able to provide Google with a redirect URL to 
  your device.

  So just give it a redirect URL for any public 
  webpage. It doesn't matter. This redirect is only
  used after login.


Download the credential you just made and save it on your Pi
in `spinkler/rpi` as `web_client_secret.json`.

This credential does not give access to your Google Account. It 
identifies the app and lets the app *request* credentials to see your 
Google Account account.


### Test the Web Server

ssh into the machine, go to the `spinkler/rpi` folder,  and type:

`gunicorn -b 0.0.0.0:5000 --pid=app.pid web_spinkler:spinkler_app`

If you get errors about missing libraries, install them. Assuming
everything works OK, try using a browser on your computer to 
access http://spinkler.local:5000/login

If you ge a login page, brilliant. Use your Google account and 
log in. If it works, you shoul be taken to a configuration page,
where you can choose the Google Calendar to use and make some 
other config change.

### Daemonize the web server.

First, if you were using the console server, disable it:

```sh
sudo systemctl stop noweb_spinkler.service
sudo systemctl disable noweb_spinkler.service
```

Now copy the web sprinkler service file:

```sh
cp systemd/web_spinkler.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable web_spinkler
sudo systemclt restart web_spinkler
```

You can see how spinkler is doing with:

```
sudo journalctl -f -u web_spinkler
```


