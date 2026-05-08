# Automated Article Delivery to Kobo with Instapaper
A simple Python pipeline that automatically sends newsletters/blogs to Instapaper such that they arrive on your Kobo e-reader each morning -- no manual steps required.

### How It Works
1. A GitHub Actions workflows runs on a schedule every morning according to specified cron jobs
2. gmail_client.py authenticates with Gmail using the Gmail API
3. Searches for unread emails from any @substack.com sender received overnight/early morning
4. Extracts the article URL from each email, cleans & resolves any links as necessary
5. Sends each finalized article URL to Instapaper via the Instapaper API
6. Marks each processed email as read in Gmail following Instapaper delivery to avoid duplicates
7. Instapaper syncs to Kobo automatically when you open "My Articles" on e-reader

### Motivation
Over the past couple of years, it's become increasingly obvious to me that we are living in a world, and an economy, that is meticulously set up to fracture our attention. Keep us scrolling, keep us distracted, and most importantly, keep us looking at OLED screens that service us advertisements every opportunity they get.

That's not the world I want to live in. I want to live in a world where I'm in control of what I see. Digital minimalism. Less ads, more true thinking. 

This project is just one way that I'm working to realize that world I want to live in. By building this, I can be intentional about the content I want to see, and don't have to open up my phone first thing in the morning to see it. I can use my e-reader to instantly get the news and other content that aligns with my interests, and I can regain autonomy for at least a couple hours after I get up out of bed. No more burning my eyes with blue light first thing and instantly getting distracted, ending up down some rabbit hole and draining away the first few precious hours of the day.

### Prerequisites
* A Kobo e-reader with Instapaper integration enabled
* An Instapaper account
* A Gmail account receiving your subscribed news
* A Google Cloud Console account
* A GitHub account

### Setup
1. Clone the repository

```
git clone https://github.com/your-username/automate-instapaper-to-ereader.git
cd automate-instapaper-to-ereader
```

2. Create and activate a python virtual environment
```
python3.11 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Configure secrets
Copy the template config file included in this repo, and fill in your subsequent values.
```
cp config.env.tmpl config.env
```

5. Setup Gmail API Credentials
    1. Navigate to Google Cloud Console
    2. Create a new project
    3. APIs & Services -> Enable APIs -> enable "Gmail API"
    4. APIs & Services -> OAuth consent screen
        * Choose "External" as user type
        * Fill in any required fields
        * In "Test users", add your Gmail address
    5. APIs & Services -> Credentials -> Create Credentials -> OAuth 2.0 Client ID
        * Select "Desktop app" as application type
        * Download the generated file, save it as "credentials.json" in your project root *** IMPORTANT ***
    6. Run the script locally for the first time
        ```
        python main.py
        ```
        On this first run, your browser should open asking to login with your Google account to grant Gmail access. If there's a warning saying the app is unverified-- click "Advanced" and then "Go to [app name]" to proceed. This is expected your first time running the application, as it is in testing mode and you are the only user (as identified in step 4 of "Setup Gmail API Credentials").

        After authenticating, token.json will be saved to the project root and the script will run.

        You will not be prompted to login again on any future runs of the application.

### GitHub Actions Setup
This workflow will automatically run ona schedule via GitHub Actions. However, this does require some added setup.

1. Add repository secrets
    * Go to your repo -> Settings -> Secrets and variables -> Actions
    * Add the following secrets
    | Secret Name         | Value                             |
    | ------------------- | --------------------------------- |
    | INSTAPAPER_USERNAME |  Your Instapaper email            |
    | INSTAPAPER_PASSWORD | Your Instapaper password          |
    | GMAIL_CREDENTIALS   | Full contents of credentials.json |
    | GMAIL_TOKEN         | Full contents of token.json       |
    * To get the contents for GMAIL_CREDENTIALS and GMAIL_TOKEN:
    ```
    cat credentials.json
    cat token.json
    ```
2. Push to main
The workflow file is required to be in the main branch in order to be picked up by GitHub Actions.

3. Trigger a manual run to verify
    * Go to your repo -> Actions -> Substack to Instapaper -> Run workflow

### Schedule
The workflow runs at the following times daily (EDT):

| cron        | Time (EDT)|
| ----------- | --------- |
| 30 10 * * * | 6:30AM    |
| 30 11 * * * | 7:30AM    |
| 30 12 * * * | 8:30AM    |
| 30 13 * * * | 9:30AM    |
| 30 14 * * * | 10:30AM   | 

### Cost
This pipeline is free to run.
    * GitHub Actions: free tier includes 2,000 min/month for private repos. This workflow uses approximately 1-2 minutes per day.
    * Gmail API: free for personal use
    * Instapaper API: free for personal use
    * Google Cloud Console: free at this scale

### Future Steps
As it currently stands, this repo only integrates Substack newsletter subscriptions being delivered to the users Gmail with Instapaper in order to receive them each morning on the Kobo e-reader.

Some next steps include:
- Expanding to other email clients such as Microsoft, Yahoo to integrate with their APIs as well for users not on GMail
- Expand integration beyond Substack-- New York Times, Washington Post, Wall Street Journal, The Atlantic, etc.
- To avoid bloating inboxes, create a topic modeling function to connect to newspaper APIs, and automatically send articles to Instapaper that align with the users interests and preferences.
