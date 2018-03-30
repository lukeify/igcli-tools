from Opt import Opt
from InstagramDataService import InstagramDataService
import time


class UserScoreboardTool:
    """
    For a given file line-separated file of instagram users, calculates the total post count for all users, and order the
    resulting output by most posts first.
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
            "mandatory": {Opt.File},
            "optional": set()
        }

    def run(self, options):
        """
        Runs the tool.

        Arguments:
            options: The options the tools needs to run this command successfully.

        Returns:
            An ordered list of users ordered by post count.
        """
        filename = options[Opt.File]

        usernames = []

        with open(filename) as f:
            for line in f:
                usernames.append(line.rstrip())

        users_by_media_count = []

        for username in usernames:
            time.sleep(2)
            try:
                media_count = self.instagram_data_service.users_user_id(username)['data']['counts']['media']
                users_by_media_count.append({
                    'username': username,
                    'count': media_count
                })
            except Exception:
                print("User could not be found: {}. Skipping...".format(username))

        for user_with_media_count in sorted(users_by_media_count, key=lambda user: user['count'], reverse=True):
            print(user_with_media_count['username'].ljust(25) + str(user_with_media_count['count']))

        return ""

    def __str__(self):
        """
        Retrieves the name of this tool.

        Returns:
            A stringified representation of this class. Just the name of the tool.
        """
        return "user-scoreboard"
