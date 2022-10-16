<div align="center">
  <h1 align="center">TweetFeed (code)</h1>

  <p align="center">
    Source code used at the repo <a href="https://github.com/0xDanielLopez/TweetFeed">TweetFeed</a>
    <br />
    <br />
    <strong>Web version at <a href="https://tweetfeed.live/">TweetFeed.live</a></strong>
  </p>
</div>

## Files

  - **tweetfeed.py** → Main script.
  - **tags.py** → Tags being searched on Twitter.
  - **whitelist.py** → Lists of whitelisted IOCs.
  - **secrets.py** → API keys.
  - **output/** → Directory with output files.

## Installation

1. Update your API keys in the **secrets.py** file. (To get API keys go to https://developer.twitter.com/apps)
2. Install requirements
```sh
$ pip3 install -r requirements.txt
```
3. Execute tweetfeed.py
```sh
$ python3 tweetfeed.py
```
## Example output

![Screenshot](https://user-images.githubusercontent.com/10616960/194862040-cc78c1aa-808a-4b91-a3b7-b810e28f9cc4.png)

## Some comments

> This is the *core* part of the code at <a href="https://github.com/0xDanielLopez/TweetFeed">TweetFeed</a>, I have tried to keep it as simple as possible.
> In the *official* code that I use I added some more regex, filters and whitelists as folks on Twitter use many formats to publish IOCs.

> Any Issue, PR or Feedback is welcome!

## Author
* [**Daniel López**](https://twitter.com/0xDanielLopez)

## Give a Star! :star:
If you like the project, please consider giving it a star!
