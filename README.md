# groot
A simple solution written in Python to move files between Google drive folders and mantain sharing properties and IDS of the original files. It works even between different domains. An authentication json file is needed for the origin folder editor user (you can obtain the authentication json file by1 following the instructions at https://developers.google.com/workspace/guides/create-credentials), the destination folder must be shared with the origin folder user as editor. Multiple istancesof the script can be used on different subfolders within the origin folder as long as different  destination subfolders exist in the destination folder.

Usage is as very simple:
python groot.py origin_folder_id destination_folder_id

The json credential file must be renamed to credentials.json and put in the same folder where you put the script.
