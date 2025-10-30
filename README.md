# What is this?
DontCheat is a software made to not cheat during exams.

**Specialized for MongoDB & Neo4j database questions.**

**Start it, click 3 times, and that's it.**

**Invisible, fast, not detectable.**
![llight](https://github.com/user-attachments/assets/f9611500-4237-416c-a2fe-dc2ac71a7104)

## How does it work?

First you need to have either a groq API key, which is free and can get at: [https://groq.com](https://groq.com) or a google gemini account to use the gemini API.

In the `.env` file you can choose which one to use, with the variable `AI_PROVIDER="gemini"` or `AI_PROVIDER="groq"`

You will need acess to VLM, in this project i use `"gemini-2.5-flash"` since it is very good and has a high limit for free users.

This software is made to be complety invisible, so you do not need to keep vs code open or even the terminal.

### 🎯 Bonus: Custom Instructions (Shift + any gesture)
* Hold **Shift** key with any of the above gestures
* Opens a dialog where you can enter custom instructions for the AI
* Examples: 
  - "Explain the query step-by-step"
  - "Show the query execution plan"
  - "Include aggregation pipeline explanation"
  - "Show alternative Cypher query"
* Works with all three gestures:
  - **Shift + 3-tap**: Custom instruction for instant analysis
  - **Shift + Option + 3-tap**: Custom instruction + save reference
  - **Shift + Control + 3-tap**: Custom instruction + analyze with reference

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

This incredible software supports **three different gestures** for maximum not cheating activities:

### Gesture 1: Instant Analysis (Normal 3-tap)
* Click anywhere on the screen **3 times** fast
* Takes screenshot and immediately analyzes it
* Perfect for standalone MongoDB/Neo4j questions
* Returns: queries, outputs, or multiple choice answers

### Gesture 2: Save Reference Context (Option + 3-tap)
* Hold **Option/Alt** key and click **3 times** fast
* Saves screenshot as reference context for future questions
* Use this for long passages/texts that multiple questions reference
* Replaces previous reference if you do it again

### Gesture 3: Analyze with Context (Control + 3-tap)
* Hold **Control** key and click **3 times** fast
* Takes screenshot of the question and analyzes it WITH the saved reference
* Perfect for answering multiple questions about the same passage
* Repeat as many times as needed

You can use any gesture as many times as you want.
when you want to stop the software just run the `stop.sh` script and it will stop.

```bash
./stop.sh
```

Wait you forgot if it is on or off? dont worry my friend I got you, just run the `status.sh` script and it will tell you if it is running or not.

```bash
./status.sh
```

**Do not use this software to cheat on exams, this was made because I needed it for an exam.**
