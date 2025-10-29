DontCheat is an software made to not each during exams.

## How does it work?

First you need to have either a groq API key, which is free and can get at: [https://groq.com](https://groq.com) or a google gemini account to use the gemini API.

In the `.env` file you can choose which one to use, with the variable `AI_PROVIDER="gemini"` or `AI_PROVIDER="groq"`

You will need acess to VLM, in this project i use `"gemini-2.5-flash"` since it is very good and has a high limit for free users.

This software is made to be complety invisible, so you do not need to keep vs code open or even the terminal.

## But how do we use it? (not to cheat of course)

  * Use only the terminal as it is faster.
  * Clone this repo
  * Navigate into the directory
  * Create a venv if you want to, I don't care.
  * Then you have to make this commands executable, you only need to run this once, otherwise you will not have the necessary permissions.
    ```bash
    chmod +x start.sh stop.sh status.sh
    ```
### How to run it?
Now we are ready to go, just run the `start.sh` script with the terminal: 

```bash
./start.sh
```

And the software will be running silently in the background you can even close the terminal if you want to. (but will have to remember to stop it later)

## What does it do?
The software is easy: 
* Click anywhere in the screen **3 times** fast.
* That's it.

The software will take a screenshot and send to the groq API to be analized by the VLM model, the model will return a banner notification with a very minimal answer, that could be an answer to a questions or something else idk.

You can continue to take screenshots and get this answers as many times as you want.
when you want to stop the software just run the `stop.sh` script and it will stop.

```bash
./stop.sh
```

Wait you forgot if it is on or off? dont worry my friend I got you, just run the `status.sh` script and it will tell you if it is running or not.

```bash
./status.sh
```

**Do not use this software to cheat on exams, this is made because i needed it for an exam.**