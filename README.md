# game-update-notifier
![image](https://github.com/user-attachments/assets/464d08a2-a5ad-4a94-b5a3-24de9ddaa334)

## Overview
A simple project to check for game updates through various platform APIs and send notifications to Telegram. Additional notification platforms will be supported in the future.

## How to Run
1. Create a `.env` file from the provided sample.
2. Build the Docker image:  
   `docker build -t game-update-notifier .`
3. Run the Docker container:  
   `docker run -d --restart unless-stopped --env-file=.env game-update-notifier`

## License
This project is licensed under the [MIT License](https://github.com/sa413x/game-update-notifier/blob/main/LICENSE).
