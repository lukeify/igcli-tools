import time

from Opt import Opt
from InstagramDataService import InstagramDataService

class LikeAnalysisTool:
    """
    Calculates the sum of likes for a user's photos and videos, along with a mean, median, mode, and most liked &
    least liked posts.
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
            "mandatory": {Opt.Username},
            "optional": {Opt.RecentPostLimit}
        }

    def run(self, options):
        """
        Runs the tool.

        Arguments:
            options: The options the tools needs to run this command successfully.

        Returns:
            The like analysis for the particular user.
        """
        user_info = self.instagram_data_service.user_info(options[Opt.Username])

        if user_info is None:
            raise Exception("API Error")

        images = []

        while True:
            time.sleep(2)
            after = None

            if len(images) > 0:
                after = images[-1]['id']

            images_from_pass = self.instagram_data_service.users_user_id_media_recent(
                user_info['data']['id'],
                count=50,
                after=after
            )['data']

            images.extend(images_from_pass)

            if len(images_from_pass) is not 50:
                break

        like_count = 0

        while images:
            like_count += images[0]['likes']['count']
            images = images[1:]

        return like_count

    def __str__(self):
        """
        Retrieves the name of this tool.

        Returns:
            A stringified representation of this class. Just the name of the tool.
        """
        return "like-analysis"
