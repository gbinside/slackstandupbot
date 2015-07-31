Slackbot for standup meeting
============================

This bot ask all team members (except the skippen ones) a list of configurable questions. Simultaneously. 

After that it report all the answers to a config defined channel.

You only need to touch the code if the `reformat` function doesn't format the output as you want.

config.ini
-----------

* copy the config.ini.dist to config.ini and edit it as you need.
* to retrieve the channel code, go to the slack page of your team, look in the html at the attribute `data-channel-id` of the `a` tag of your desidered channel es: `data-channel-id="C082PN93M"`
* same for the user code to skip, but the attribute is `data-member-id`
* optionally you can retrieve the channels list by using `python list.py channels`
* optionally you can retrieve the users list by using `python list.py users`
* change the `reformat` function to your needs, the default is:

![example](https://raw.githubusercontent.com/gbinside/slackstandupbot/master/screenshot/001.png)

Run
-----------

* first create a config.ini like said before
* run `python slackstandupbot.py`

TODO
----------

* start the threads only N at a time, not all togheter; if you have a lot of member of your team, you can spawn too much threads.
