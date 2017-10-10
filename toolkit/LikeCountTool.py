from Opt import Opt
from InstagramDataService import InstagramDataService

class LikeCountTool():
    """
    """
    def __init__(self, instagram_data_service: InstagramDataService) -> None:
        """
        """
        self.instagram_data_service = instagram_data_service

    def requested_options(self):
        """
        The options needed and preferred for the tool to run successfully.

        Returns:
            A dictionary containing two sets, `mandatory`, and `optional`.
        """
        return {
            "mandatory": { Opt.Username },
            "optional": set()
        }


    def run(self, options):
        """
        """
        user_search_results = self.instagram_data_service.users_search(q=options[Opt.Username])

        user = None
        for user_search_result in user_search_results['data']:
            if user_search_result['username'] == options[Opt.Username]:
                user = user_search_result
                break

        if user is None:
            raise Exception("API Error")

        user_images = self.instagram_data_service.users_user_id_media_recent(user['id'], count=200)['data']

        like_count = 0
        while user_images:
            like_count += user_images[0]['likes']['count']
            user_images = user_images[1:]

        return like_count

    def __str__(self):
        """
        """
        return "like-count"
