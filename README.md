Watcher is an automated movie NZB searcher and snatcher. You can add a list of wanted movies and Watcher will automatically send the NZB to Sabnzbd or NZBGet. Watcher also has basic post-processing capabilities such as renaming and moving.

Watcher is a work in progress and plans to add more features in the future, but we will always prioritize speed and stability over features.


## Installation

Watcher requires [Python 2.7.9](https://www.python.org/) or newer. If you are running OSX or *nix you probably have python 2.7 already. If you do not, or are on Windows, make sure you install Python.

It is also strongly recommended that you install [GIT](http://git-scm.com/). This will allow you to update much more easily.

**Download the required files using GIT:**

If you choose to use Git follow these steps.

* Open a terminal and cd to the directory you in which you want to install Watcher.
* Run `git clone https://github.com/nosmokingbandit/watcher.git`
* Start Watcher using `python watcher/watcher.py`
* Open a browser and navigate to `localhost:9090`

**Download ZIP:**

If you do not wish to use Git, follow these steps.

* Open your browser and go to `https://github.com/nosmokingbandit/watcher`
* Click on the green `Clone or download` button and click `Download ZIP`
* Once done downloading, extract the ZIP to the location in which you want Watcher installed
* Open a terminal and cd to the Watcher directory.
* Start Watcher using `python watcher/watcher.py`
* Open a browser and navigate to `localhost:9090`


## Usage

You can add the following arguments to Watcher when running the Python script.

Run the server as a daemon (only available for *nix based operating systems).
`$ watcher.py --daemon`

Change address to bind to.
`$ watcher.py --address 0.0.0.0`

Change port to host on.
`$ watcher.py --port 9090` 9090 Port to bind to.

Open browser on launch.
`$ watcher.py --browser`

Change path to config file. If not present, one will be created.
`$ watcher.py --conf path/to/config.cfg`

Change path of log directory.
`$ watcher.py --log path/to/logs/`

## Post-Processing

Watcher supports post-processing for Sabnzb and NZBGet. To enable, copy the appropriate script from `watcher/post scripts` to your downloader's scripts directory.

For *Sabnzb*, edit the script file and add your api keys and server information. Then, in Sabnzb, disable `Post-Process Only Verified Jobs`, create a new Category using the same category name you have in Watcher. Select the post-processing script and save.

For *NZBGet*, go to Settings and set up a Category with the same category name you have in Watcher. In `Post-Script` select the Watcher post-processing script. In the left column, select Watcher and add your server information. Save your settings and restart NZBGet.
