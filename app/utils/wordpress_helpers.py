import requests
import json

class wp_domain:
    
    def __init__(self, domain):
        self.domain = domain

    
    def get_all_wordpress_pages(self):
        """ 
        Fetches all pages from a WordPress site using its REST API.

        Args:
            url (str): The base URL of the WordPress site.
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            list: A list of dictionaries, each representing a WordPress page.
        """

        auth = (self.domain.domain_login_username, self.domain.domain_login_password)
        headers = {'Content-Type': 'application/json'}
        api_url = f"{self.domain.domain_name}/wp-json/wp/v2/pages"

        all_pages = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            params = {'page': page}
            response = requests.get(api_url, auth=auth, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                all_pages.extend(data)
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                page += 1
            else:
                print(f"Error fetching pages: {response.status_code}")
                break
        return all_pages
    

    def get_all_wordpress_posts(self):
        """ 
        Fetches all pages from a WordPress site using its REST API.

        Args:
            url (str): The base URL of the WordPress site.
            username (str): The username for authentication.
            password (str): The password for authentication.

        Returns:
            list: A list of dictionaries, each representing a WordPress page.
        """

        auth = (self.domain.domain_login_username, self.domain.domain_login_password)
        headers = {'Content-Type': 'application/json'}
        api_url = f"{self.domain.domain_name}/wp-json/wp/v2/posts"

        all_posts = []
        post = 1
        total_posts = 1

        while post <= total_posts:
            params = {'posts': post}
            response = requests.get(api_url, auth=auth, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                all_posts.extend(data)
                total_posts = int(response.headers.get('X-WP-TotalPages', 1))
                post += 1
            else:
                print(f"Error fetching pages: {response.status_code}")
                break
        return all_posts
    


class pages(wp_domain):

    def __init__(self, id):
        self.page_id = id

    
    def update_meta_tag(self):
        pass

    def update_og_tags(self):
        pass

    def generate_meta_tags(self):
        pass

    def generate_og_tags(self):
        pass