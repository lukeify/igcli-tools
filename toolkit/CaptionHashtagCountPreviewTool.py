from Opt import Opt
from InstagramDataService import InstagramDataService


class CaptionHashtagCountPreviewTool:
    """
    Calculates the amount of hashtags in a given caption, provided by the user.
    """
    def __init__(self, instagram_data_service: InstagramDataService) -> None:
        """
        Initialization.
        """
        self.instagram_data_service = instagram_data_service

    @staticmethod
    def requested_options():
        """
        The options needed and preferred for the tool to run successfully.

        Returns:
            A dictionary containing two sets, `mandatory`, and `optional`.
        """
        return {
            "mandatory": {Opt.Caption},
            "optional": set()
        }

    def run(self, options):
        """
        """
        words_in_caption = options[Opt.Caption].split(" ")

        # lambda to determine hashtags in caption
        hashtags_in_caption = []

        if len(hashtags_in_caption) < 30:
            pass
        elif len(hashtags_in_caption) == 30:
            pass
        else:
            return "Your caption contains {} hashtags, and will fail to be posted to Instagram as the limit is 30 " \
                   "per caption/comment".format(len(hashtags_in_caption))

    def __str__(self):
        """
        Retrieves the name of this tool.

        Returns:
            A stringified representation of this class. Just the name of the tool.
        """
        return 'caption-hashtag-count-preview'
