# JARVIS Feature Guide

## Jarvis kya kar sakta hai?

Jarvis ek Windows AI assistant hai jo aapki voice ya typed command ko samajhkar everyday tasks ko jaldi complete karta hai. Neeche har feature ko simple language mein explain kiya gaya hai.

## 1. Voice Control

Mic button dabaiye aur normal language mein boliye. Jarvis aapki command sunega aur answer ya action karega.

**Try:** `open chrome` · `what time is it`

## 2. AI Chat

Kisi bhi topic par sawal poochhiye—study, ideas, coding, explanations, ya general help. Jarvis AI reply chat history mein save bhi hota hai.

**Try:** `explain quantum computing` · `write a Python calculator`

## 3. Apps aur Websites Open Karna

Apne installed apps ya saved websites ko naam se open kijiye. Jarvis pehle saved command check karta hai, phir Windows se open karne ki koshish karta hai.

**Try:** `open calculator` · `open youtube`

## 4. YouTube Play

Song, video, ya playlist ka naam boliye. Jarvis YouTube par search karke playback start karega.

**Try:** `play perfect on youtube` · `play lo-fi music on youtube`

## 5. Google Search

Koi bhi cheez web par khojni ho to direct command boliye. Jarvis aapke default browser mein Google search khol dega.

**Try:** `search Python tutorial` · `google restaurants near me`

## 6. Live Weather

Apne city ka current temperature aur weather condition poochhiye.

**Try:** `weather in Lucknow` · `what is the weather in Delhi`

> Weather ke liye `.env` mein `OPENWEATHER_API_KEY` set hona zaroori hai.

## 7. Memory

Jarvis ko koi important detail yaad karwaiye aur baad mein wahi detail poochh lijiye. Data aapke local Jarvis database mein rehta hai.

**Try:** `remember my college is XYZ` · `what is my college`

## 8. WhatsApp Actions

Saved contacts ko WhatsApp message, voice call, ya video call start kijiye.

**Try:** `send message to Rahul` · `video call Rahul`

> Contact aapki local contacts list mein saved hona chahiye.

## 9. Secure Access

Jarvis ko face authentication aur personal pattern lock se secure rakhiye. Pattern change ya remove bhi settings se kiya ja sakta hai.

**Try:** `unlock Jarvis` · `change pattern`

## Feature UI kaise kholein?

Main Jarvis screen par chat icon ke paas **grid icon** dabaiye. Wahan har feature ki short explanation aur copy-able example command mil jayegi.

## Setup Note

AI Chat ke liye `.env` mein `GROQ_API_KEY` set kijiye. Aapki private API keys, contacts, memory aur pattern-lock file GitHub par upload nahi honi chahiye.
