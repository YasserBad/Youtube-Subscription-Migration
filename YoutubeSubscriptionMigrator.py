import os, pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


subscription_file = "subscriptions.txt"

def pickle_file_name(
        api_name = 'youtube',
        api_version = 'v3',
        account="default"):
    return f'token_{api_name}_{api_version}_{account}.pickle'

def load_credentials(
        api_name = 'youtube',
        api_version = 'v3',
        account="default"):
    pickle_file = pickle_file_name(
        api_name, api_version,account)

    if not os.path.exists(pickle_file):
        return None

    with open(pickle_file, 'rb') as token:
        return pickle.load(token)

def save_credentials(
        cred, api_name = 'youtube',
        api_version = 'v3',
        account="default"):
    pickle_file = pickle_file_name(
        api_name, api_version,account)

    with open(pickle_file, 'wb') as token:
        pickle.dump(cred, token)

def create_service(
        client_secret_file, scopes,
        api_name = 'youtube',
        api_version = 'v3',
        account="default"):
    print(client_secret_file, scopes,
        api_name, api_version,
        sep = ', ')

    cred = load_credentials(api_name, api_version,account)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, scopes)
            cred = flow.run_console()

    save_credentials(cred, api_name, api_version,account)

    try:
        service = build(api_name, api_version, credentials = cred)
        print(api_name, 'service created successfully')
        return service
    except Exception as e:
        print(api_name, 'service creation failed:', e)
        return None

def fetch_subscriptions(sub_file):
    nextPageToken = ""
    file = None
    youtube = create_service("source.json",
        ["https://www.googleapis.com/auth/youtube.readonly"], account="source")
    if not youtube: return

    print("Fetching Subscriptions from the source account, Please be patient.")

    while nextPageToken != None:
        request = youtube.subscriptions().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults = 50,
                pageToken = nextPageToken,
                fields= "nextPageToken, items(snippet(resourceId(channelId)))"
            )
        response = request.execute()

        for i in range(len(response['items'])):
            # Write channel IDs in the file
            with open(sub_file, "a", encoding="utf-8") as file:
                file.write(str(response['items'][i]['snippet']['resourceId']['channelId']) + "\n")
        file.close()
        if "nextPageToken" in response:
            nextPageToken = response['nextPageToken']
        else:
            nextPageToken = None


def subscribe_to_channels(channels):
    response = None
    youtubeSub = create_service("target.json",["https://www.googleapis.com/auth/youtube.force-ssl"], account="target")
    if not youtubeSub: return

    print("Subscribing to channels has started, please be patient")

    for channel_id in channels:
        if channel_id.strip() != None:
            request = youtubeSub.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                    "resourceId": {
                        "kind": "youtube#channel",
                        "channelId": channel_id
                        }
                        }
                    }
                )
            try:
                response = request.execute()
                print("Subscribing to " + response['snippet']['title'])
            except:
                print("Subscription duplicated. Skipped")

def main():
    # Check if there is a file that has the subscriptions (The program has been already ran)
    if os.path.exists(subscription_file):
        restart = input("A file containing subscriptions has been detected. Enter Y if you want to use it or N if you want to start over ==> ")
        if restart.lower() == "y":
            pass
        elif restart.lower() == "n":
            # Clear any logs saved in this file
            with open(subscription_file, 'w', encoding="utf-8") as file:
                file.write(" ")
                fetch_subscriptions(subscription_file)
        else:
            print("Command unknonwn")
            main()
    else:
        fetch_subscriptions(subscription_file)

    with open(subscription_file, "r", encoding="utf-8") as file:
        file_content = file.read()
        subscriptions = file_content.splitlines()

    subscribe_to_channels(subscriptions)

if __name__ == '__main__':
    main()