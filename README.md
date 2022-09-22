# Youtube-Subscription-Migration
A simple python script that transfers subscriptions from a populated account to a new (empty) account.

# How to use the script:
This is a script that uses the Youtube Data API V3.
1- Get an API OAuth2.0 key for both of the accounts (From Google Cloud Services)
2- Name them source.json and target.json (source.json being for the populated account and target.json being the key for the empty account)
3- Put them in the same folder as the YoutubeSubscriptionMigrator.py
4- Run the script.
5- You'll have to authorize the connection as the script prompts you to (You only have to do it once, because the tokens will be saved in a file)
