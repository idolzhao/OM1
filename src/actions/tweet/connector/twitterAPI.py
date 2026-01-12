import logging
import os
import warnings

from dotenv import load_dotenv

from actions.base import ActionConfig, ActionConnector
from actions.tweet.interface import TweetInput


class TweetAPIConnector(ActionConnector[ActionConfig, TweetInput]):
    """
    Connector for Twitter API.

    This connector integrates with Twitter API v2 to post tweets from the robot.
    """

    def __init__(self, config: ActionConfig):
        """
        Initialize the Twitter API connector.

        Parameters
        ----------
        config : ActionConfig
            Configuration for the action connector.
        """
        super().__init__(config)

        load_dotenv()

        # Suppress tweepy warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            import tweepy  # type: ignore

            # Validate environment variables exist
            consumer_key = os.getenv("TWITTER_API_KEY")
            consumer_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                missing_vars = []
                if not consumer_key:
                    missing_vars.append("TWITTER_API_KEY")
                if not consumer_secret:
                    missing_vars.append("TWITTER_API_SECRET")
                if not access_token:
                    missing_vars.append("TWITTER_ACCESS_TOKEN")
                if not access_token_secret:
                    missing_vars.append("TWITTER_ACCESS_TOKEN_SECRET")
                raise ValueError(
                    f"Missing required Twitter API credentials: {', '.join(missing_vars)}"
                )

            self.client = tweepy.Client(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
            )

    async def connect(self, output_interface: TweetInput) -> None:
        """
        Send tweet via Twitter API.

        Parameters
        ----------
        output_interface : TweetInput
            The TweetInput interface containing the tweet text.
        """
        try:
            # Log the tweet we're about to send
            # FIXED: Changed from output_interface.tweet to output_interface.action
            tweet_to_make = {"action": output_interface.action}
            logging.info(f"SendThisToTwitterAPI: {tweet_to_make}")

            # Send tweet
            # FIXED: Changed from output_interface.tweet to output_interface.action
            response = self.client.create_tweet(text=output_interface.action)
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            logging.info(f"Tweet sent successfully! URL: {tweet_url}")

        except tweepy.TweepyException as e:
            logging.error(f"Twitter API error while sending tweet: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while sending tweet: {str(e)}")
            raise
