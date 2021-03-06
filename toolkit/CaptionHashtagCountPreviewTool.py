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
        hashtags_in_caption = [x for x in words_in_caption if x[0] is '#']

        hashtag_count = len(hashtags_in_caption)

        if hashtag_count < 30:
            return "Your caption contains {} {}, you have {} {} remaining."\
                .format("hashtag" if hashtag_count is 1 else "hashtags",
                        hashtag_count, 30 - hashtag_count, "hashtag" if 30 - hashtag_count is 1 else "hashtags")
        elif hashtag_count == 30:
            return "Your caption has the maximum amount of 30 hashtags per comment. To include additional hashtags " \
                   "you will need to post another comment."
        else:
            return "Your caption contains {} hashtags, and will fail to be posted to Instagram as the limit is 30 " \
                   "per caption/comment".format(hashtag_count)

    def __str__(self):
        """
        Retrieves the name of this tool.

        Returns:
            A stringified representation of this class. Just the name of the tool.
        """
        return 'caption-hashtag-count-preview'
