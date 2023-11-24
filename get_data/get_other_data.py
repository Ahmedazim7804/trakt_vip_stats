from trakt.core import BASE_URL, CORE
from urllib.parse import urljoin

def all_time_stats():

    def get_comments():
        page = 1
        comments = 0
        while True:
            url = urljoin(BASE_URL, f'users/***REMOVED***/comments/all/all?include_replies=False&page={page}')
            data = CORE._handle_request(url=url, method='get')

            if not data:
                break
                
            comments += len(data)

            page += 1
        
        return comments

    url = urljoin(BASE_URL, 'users/ahmedazim7804/stats')
    data = CORE._handle_request(url=url, method='get')

    plays : int = data['movies']['plays'] + data['episodes']['plays']
    hours : float = round(((data['movies']['minutes'] + data['episodes']['minutes']) / 60), 0)
    collected : int = data['movies']['collected'] + data['episodes']['collected']
    ratings : int = data['ratings']['total']
    lists : int = len(CORE._handle_request(url=urljoin(BASE_URL, 'users/ahmedazim7804/lists'), method='get'))
    comments : int = get_comments()

    return {
        'plays': plays,
        'hours': hours,
        'collected': collected,
        'ratings': ratings,
        'lists': lists,
        'comments': comments
        }

if __name__ == '__main__':
    import sys
    sys.path.append('/home/ajeem/Development/projects/python/traktData')
    from main import authenticate

    username = "***REMOVED***"
    client_id = "***REMOVED***"
    client_secret = "***REMOVED***"
    authenticate(username, client_id=client_id, client_secret=client_secret)

    print(all_time_stats())