## Hoyolab Auto Check-in

This Python script automates the daily check-in process for Hoyolab, allowing you to claim rewards for Genshin Impact, Honkai: Star Rail and Zenless Zone Zero without manually visiting the website. It also supports sending notifications to Discord using webhooks.

### Features

* **Automated Check-in:** Automatically checks in for supported games and claims daily rewards.
* **Discord Notifications:** Sends detailed check-in results to a Discord channel via webhook (optional).

### Setup

1. [Forked from Satellaa/Hoyolab-auto-checkin](https://github.com/Satellaa/Hoyolab-auto-checkin)
2. **Obtain Your Hoyolab Cookie:**
   * Open your web browser and navigate to the Hoyolab Daily Check-in page.
   * Log in to your Hoyolab account.
   * Open the browser's developer tools (usually by pressing F12).test
   * Claim your daily reward.
   * Go to the "Network" tab in the developer tools.
   * Look for a request to a URL that contains the word "sign" (e.g., `https://sg-hk4e-api.hoyolab.com/event/sol/sign`).
   * Click on that request to view its details.
   * In the "Request Headers" section, find the `Cookie` header and copy its entire value. This is your Hoyolab cookie. 

3. **Get Your User Agent:**
   * Open your web browser and search for "my user agent" on Google.
   * Copy the user agent string that appears in the search results.

4. **Set Secrets in your repository:**
   * Follow [.env_exemple](.env_exemple)

5. **Add Binarie Code:**
   * For environment
      ```
      sudo apt update
      sudo apt install python3-venv python3-pip
   
      python3 -m venv venv
      source venv/bin/activate
   
      pip install -r requirements.txt
      pip install pyinstaller
      ```
   * Optional: 
      ```
      pyinstaller --onefile --add-data ".env:." main.py
      ```
   * Cron:
     ``` 
         crontab -e
        ```
      ```
        30 18 * * * cd /home/user/path/dist && ./main >> /home/path/aaa.log 2>&1
      ```
   

### Important Notes

* **Cookie Security:** Keep your Hoyolab cookie safe and secure. Do not share it with anyone.
* **Supported Games:** The script currently supports Genshin Impact, Honkai: Star Rail and Zenless Zone Zero.
* **API Changes:** Hoyolab's API may change in the future, potentially breaking the script. Updates may be required to keep it functional.

### Disclaimer

This script is provided for convenience purposes only. Use it at your own risk. The author is not responsible for any issues or consequences that may arise from using this script.
