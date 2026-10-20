# MTGO Replay Analysis

This repository is a GUI tool for assisting in analysis MTGO log data. It will automatically
read logs, and record data from them such as game and match wins, mulligans, cards played,
and even card win rates with filtering by date and format

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Usage](#usage)

## Installation
Install python>=3.14.4 then run the following

``` 
git clone https://github.com/cnalty/mtgo_replay_analysis.git
cd mtgo_replay_analysis
python pip install . 

python -m mtgo_replay_analysis --replay_folder {location of mtgo logs} --username {mtgo username}
```


## Getting Started

Once the program is installed the database can be run using

`python -m mtgo_replay_analysis`

### Arguments
There are 3 arguments that can be used with this command 
> --db : This argument is used if you want a custom database location, it must be entered every run if 
>  you are not using the default
> 
> --replay_folder : This is the location of your mtgo log files. These can be found in "AppData/Local/Apps/2.0/Data". 
> Once you've navigated here you can search for "Match_GameLog_" to find the full location.
> This location will be remembered after the initial run
> 
> --username : Your mtgo username, this will be remembered after the initial run


## Usage

