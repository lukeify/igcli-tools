import urllib.parse

import lxml
import requests

class InstagramDataService():

    """
    Provides
    """

    def users_self(self):
        """
        For the authenticated user, returns their profile details including user_id,
        username, fullname, profile picture, biography, website, and media counts.

        Mimics https://www.instagram.com/developer/endpoints/users/#get_users_self

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_self
        """
        pass


    def users_user_id(self, user_id):
        """
        """
        pass


    def users_self_media_recent(self, **kwargs):
        """
        For the authenticated user, returns the recent media from their
        profile up to count items, provided they are within the bounds of the maximum
        or minimum ID, provided those values are set.

        If no count is provided, will return up to 12 results. If no maximum or
        minimum ID is provided, the most recent media will be returned.

        Mimics https://www.instagram.com/developer/endpoints/users/#get_users_media_recent_self

        Args:
            user_id: The ID of the user to retrieve media results for.

        Keyword Arguments:
            max_id: Allows results up to and including the maximum media ID
                provided. Defaults to None.

            min_id: Allows results down to and including the minimum media ID
                provided. Defaults to Done.

            count: The number of media entities to retrieve, defaults to 12.

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_media_recent_self
        """
        return {
            'data': [{

            }]
        }


    def users_user_id_media_recent(self, user_id, **kwargs):
        """
        For the user with the provided user_id, returns the recent media from their
        profile up to count items, provided they are within the bounds of the maximum
        or minimum ID, provided those values are set.

        If no count is provided, will return up to 12 results. If no maximum or
        minimum ID is provided, the most recent media will be returned.

        Mimics https://www.instagram.com/developer/endpoints/users/#get_users_media_recent

        Args:
            user_id: The ID of the user to retrieve media results for.

        Keyword Args:
            after: Includes `count` results after the ID of the image provided in after. Defaults to none if not included.

            count: The number of media entities to retrieve, defaults to 12.

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_media_recent

        Notes:
            Divergences from the Instagram API: `max_id` has been subsumed by `after`, and `min_id` is no longer available.
        """
        if user_id is None:
            raise Exception("Please provide a user id")

        image_count_to_fetch = 12
        if 'count' in kwargs:
            image_count_to_fetch = kwargs['count']

        images_after_id = None
        if 'after' in kwargs:
            images_after_id = kwargs['after']

        variables = '{{"id":{},"first":{}}}'.format(user_id, image_count_to_fetch) if images_after_id is None else '{{"id":{},"first":{}, "after": {}}}'.format(user_id, image_count_to_fetch, images_after_id)

        r = requests.get('https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables={}'.format(urllib.parse.quote(variables, safe='')))

        # Ensure status code is 200
        if r.status_code is not 200:
            raise Exception("Instagram responded with {} status code".format(str(r.status_code)))

        json_response = r.json()

        images = json_response['data']['user']['edge_owner_to_timeline_media']['edges']

        # Transform data to make it sane
        transformed_images = []
        for image in images:

            # Pull across useful properties
            transformed_image = {
                "id": image['node']['id'],
                "ceated_at_timestamp": image['node']['taken_at_timestamp'],
                "caption": None, # Set later if applicable
                "comments": {
                    "count": image['node']['edge_media_to_comment']['count'],
                    "is_disabled": image['node']['comments_disabled']
                },
                "shortcode": image['node']['shortcode'],
                "dimensions": {
                    "width": image['node']['dimensions']['width'],
                    "height": image['node']['dimensions']['height'],
                },
                "display_url": image['node']['display_url'],
                "likes": {
                    "count": image['node']['edge_media_preview_like']['count']
                },
                "owner": {
                    "id": image['node']['owner']['id']
                },
                "thumbnail_src": image['node']['thumbnail_src'],
                "thumbnail_resources": image['node']['thumbnail_resources'],
                "is_video": image['node']['is_video']
            }

            # Only include video_view_count if the entity is a video
            if transformed_image["is_video"]:
                transformed_image['video_view_count'] = image['node']['video_view_count']

            # Set the text of the caption if one exists
            if len(image['node']['edge_media_to_caption']['edges']) != 0:
                transformed_image["caption"] = {
                    "text": image['node']['edge_media_to_caption']['edges'][0]["node"]["text"]
                }

            transformed_images.append(transformed_image)

        return {
            'data': transformed_images
        }


    def users_self_media_liked(self):
        """
        """
        pass

    def users_search(self, **kwargs):
        """
        Provides search results for a provided query, delimited to the number of results requested by `count`. If no
        count is provided, returns as many results as provided by the call to Instagram's servers.

        Mimics https://www.instagram.com/developer/endpoints/users/#get_users_search

        Keyword Args:
            q: The query to search on.
            count: The maximal number of users to return.

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_search

        Notes:
            Divergences from the Instagram API: 1) Instagram has dropped support for first name and last names on the
            platform in lieu of fullnames. 2) Instagram now provides a lot more data on each returned user via search. This
            is included in the result.
        """

        # Ensure a search query is provided.
        if 'q' not in kwargs:
            raise Exception("Please provide a search query")

        # Make the request
        r = requests.get('https://instagram.com/web/search/topsearch/?context=blended&query={}'.format(kwargs['q']))

        # Ensure status code is 200
        if r.status_code is not 200:
            raise Exception("Instagram responded with {} status code".format(str(r.status_code)))

        # Parse response into JSON
        json_response = r.json()

        # delimit the number of users we take.
        users = json_response['users']
        if 'count' in kwargs:
            users = users[:kwargs['count']]

        transformed_users = []
        for user in users:
            user['user']['id'] = int(user['user'].pop('pk', None))
            transformed_users.append(user['user'])

        return {
            'data': transformed_users
        }
