import urllib.parse
import re
import hashlib
import json
import requests


def unauthenticated(fn):
    """
    Python decorator to indicate that the function is an unauthenticated endpoint.
    """
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def authenticated(fn):
    """
    Python decorator to indicate that the function is an authenticated endpoint requiring a user login and password.
    """
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


class InstagramDataService:
    """
    InstagramDataService.
    """

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) ' \
                 'Version/11.0.1 Safari/604.3.5'
    rhx_gis = None
    csrf_token_cookie = None
    session = requests.Session()

    def __init__(self):
        """
        Initialize our Instagram session by making a request to the homepage. From here, grab the rhx_gis special token
        and set it on the InstagramDataService class. This special token is needed to make future requests over Instagram's
        private web API.
        """
        res = self.session.get('https://www.instagram.com', headers={
            'User-Agent': self.user_agent
        })
        regex_match = re.search(r'"rhx_gis":"(?P<rhx_gis>[a-f0-9]{32})"', res.text)
        if regex_match:
            self.rhx_gis = regex_match.group('rhx_gis')

    def build_signature(self, query_variables):
        """
        Given the magic rhx_gis string first retrieved in an initial instagram request, and the query variables being
        sent in the request, build a magic signature to get around Instagram's webscraping blocking attempts.

        Args:
            query_variables: The query variables of the request, as a string.

        Returns:
            An MD5 hash representing the rhx_gis string and the query variables of the request.
        """
        m = hashlib.md5()
        m.update('{rhx_gis}:{variables}'.format(rhx_gis=self.rhx_gis, variables=query_variables).encode('utf-8'))
        return m.hexdigest()

    def request(self, **kwargs):
        """
        Makes an instagram HTTP request, properly formatting any query variables provided and incorporating the custom
        X-Instagram-GIS and User-Agent headers required to be persisted between requests by Instagram.

        Keyword Args:
            endpoint: The type of request to instagram this is. Can be a string of 'username', 'search', or 'graphql'.

            username: If the endpoint kwarg is set to 'username', the username kwarg must be provided.

            query_params: A dict of query parameters commonly used in all Instagram requests. If endpoint kwarg is set to
                'username', this will be ignored.

            query_hash: The Instagram GraphQL identifier used to make the request. Must be provided if endpoint is set as
            'graphql', will be ignored otherwise.

            query_variables: A dict of query parameters commonly used in graphql Instagram requests. Before a request is made
                to Instagram's servers, this dict is translated into a URL-safe string. Most be provided if endpoint is set as
                'graphql', will be ignored otherwise.

        Returns:
            The raw response from Instagram's servers.
        """
        endpoint_url = None
        signature_var = None
        query_params = kwargs.pop('query_params', {})

        if kwargs['endpoint'] is "username":
            if 'username' not in kwargs:
                raise Exception("username kwarg not provided for a username endpoint")

            endpoint_url = 'https://www.instagram.com/' + kwargs['username'] + '/'
            signature_var = urllib.parse.urlparse(endpoint_url).path
            query_params = {
                '__a': '1'
            }

        elif kwargs['endpoint'] is "search":
            endpoint_url = 'https://www.instagram.com/web/search/topsearch/'

        elif kwargs['endpoint'] is "graphql":
            if 'query_hash' not in kwargs:
                raise Exception("query_hash kwarg not provided for a graphql endpoint")

            endpoint_url = 'https://www.instagram.com/graphql/query/'
            query_params['query_hash'] = kwargs['query_hash']

            signature_var = query_params['variables'] = json.dumps(kwargs['query_variables'])

        return self.session.get(endpoint_url + "?{}".format(urllib.parse.urlencode(query_params)), headers={
            'User-Agent': self.user_agent,
            'X-Instagram-GIS': self.build_signature(signature_var)
        })

    @authenticated
    def users_self(self):
        """
        For the authenticated user, returns their profile details including user_id,
        username, fullname, profile picture, biography, website, and media counts.

        Mimics https://www.instagram.com/developer/endpoints/users/#get_users_self

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_self
        """
        pass

    @unauthenticated
    def user_info(self, username):
        """
        For the user with the provided username, returns their user details, including media counts, website, & bio.

        Args:
            username: The username of the user to retrieve details for.

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users
        """
        if username is None:
            raise Exception("Please provide a username")

        r = self.request(endpoint='username', username=username)

        # Ensure status code is 200
        if r.status_code is not 200:
            raise Exception("Instagram responded with {} status code".format(str(r.status_code)))

        json_response = r.json()

        return {
            'data': {
                'id': json_response['graphql']['user']['id'],
                'username': json_response['graphql']['user']['username'],
                'full_name': json_response['graphql']['user']['full_name'],
                'profile_picture': json_response['graphql']['user']['profile_pic_url_hd'],
                'bio': json_response['graphql']['user']['biography'],
                'website': json_response['graphql']['user']['external_url'],
                'counts': {
                    'media': json_response['graphql']['user']['edge_owner_to_timeline_media']['count'],
                    'follows': json_response['graphql']['user']['edge_follow']['count'],
                    'followed_by': json_response['graphql']['user']['edge_followed_by']['count']
                }
            }
        }

    @authenticated
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

    @unauthenticated
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
            after: Includes `count` results after the ID of the image provided in after.
            Defaults to none if not included.

            count: The number of media entities to retrieve, defaults to 12.

        Returns:
            JSON formatted similarly to https://www.instagram.com/developer/endpoints/users/#get_users_media_recent

        Notes:
            Divergences from the Instagram API: `max_id` has been subsumed by `after`,
            and `min_id` is no longer available.
        """
        if user_id is None:
            raise Exception("Please provide a user id")

        image_count_to_fetch = 12

        if 'count' in kwargs:
            if kwargs['count'] > 50:
                raise Exception("count cannot be greater than 50")

            image_count_to_fetch = kwargs['count']

        images_after_id = None
        if 'after' in kwargs:
            images_after_id = kwargs['after']

        variables = {
            "id": user_id,
            "first": image_count_to_fetch
        }

        if images_after_id is not None:
            variables['after'] = images_after_id

        r = self.request(endpoint='graphql', query_hash='42323d64886122307be10013ad2dcc44', query_variables=variables)

        # Ensure status code is 200
        if r.status_code is not 200:
            raise Exception("Instagram responded with {} status code".format(str(r.status_code)))

        images = r.json()['data']['user']['edge_owner_to_timeline_media']['edges']

        # Transform response data from instagram to make it sane.
        transformed_images = []

        for image in images:
            # Pull across useful properties
            transformed_image = {
                "id": image['node']['id'],
                "created_at_timestamp": image['node']['taken_at_timestamp'],
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

    @authenticated
    def users_self_media_liked(self):
        """
        """
        pass

    @unauthenticated
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
            platform in lieu of fullnames. 2) Instagram now provides a lot more data on each returned user via search.
            This is included in the result.
        """

        # Ensure a search query is provided.
        if 'q' not in kwargs:
            raise Exception("Please provide a search query")

        # Make the request
        r = self.request(endpoint='search', query_params={
            'context': 'blended',
            'query': kwargs['q']
        })

        # Ensure status code is 200
        if r.status_code is not 200:
            raise Exception("Instagram responded with {} status code".format(str(r.status_code)))

        # delimit the number of users we take.
        users = r.json()['users']
        if 'count' in kwargs:
            users = users[:kwargs['count']]

        transformed_users = []
        for user in users:
            user['user']['id'] = int(user['user'].pop('pk', None))
            transformed_users.append(user['user'])

        return {
            'data': transformed_users
        }
