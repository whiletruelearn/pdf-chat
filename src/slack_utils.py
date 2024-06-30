from slack_sdk import WebhookClient
from slack_sdk.errors import SlackApiError
import os
import logging

class SlackUtils:
    def __init__(self):
        self.client = WebhookClient(os.environ['SLACK_HOOK'])
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def post_message(self, message: str) -> None:
        """
        Post a message via the specified webhook to the channel
        Args:
            message (str): The message to post to Slack.
        """
        try:
            self.client.send(text=message)
            self.logger.info(f"Message posted to Slack channel ")
        except SlackApiError as e:
            self.logger.error(f"Error posting message to Slack: {e}")

    