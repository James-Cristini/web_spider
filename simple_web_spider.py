import sys
from multiprocessing import Pool
import bs4 as bs
import requests
import random
import string


# Get a random starting URL using a random 3-letter string
def random_starting_url():
    starting = "".join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(3))
    url = ''.join(['http://www.', starting, '.com'])
    return url

# Handles any local links on a site (e.g links that direct the user to other parts of the site with the same base url)
def handle_local_links(url, link):
    if link.startswith('/'):
        return "".join(url, link)
    else:
        #This also returns any potential "links" that do not start with "/" and will need to be handled
        return link

# Finds and stores all links on a page
def get_links(url):
    try:
        # Use requests and beautiful soup to parse and pull out all links in the body of a web page
        resp = requests.get(url)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        body = soup.body
        # Finds all links (hrefs) within <a> tags
        links = [link.get('href') for link in body.find_all('a')]
        # Run each link through handle_local_links()
        links = [handle_local_links(url, link) for link in links]
        #Encode each link as ascii string
        links = [str(link.encode('ascii')) for link in links]
        return links

    # Handle exceptions for known errors
    except TypeError as e:
        print e
        print "Type error, probably tried to iterate over a None"
        return []
    except IndexError as e:
        print e
        print "Probably didnt find any useful links, returning an empty link"
        return []
    except AttributeError as e:
        print e
        print "Likely got None for links so we're throwing this exception"
        return []
    except Exception as e:
        print "** Error---", str(e)
        # Shouid log any erros that pass through here
        return []

# Define main function using multiprocessing
def main(num=5):
    # How many links will be tested, user can input a number via command line, otherwise it'll default to 5
    try:
        how_many = int(num[1])
        print "Checking {} urls".format(how_many)
    except ValueError:
        print "Not an integer; checking 5 urls instead"
        how_many = 5
    except IndexError:
        print "You didnt enter a number, no worries we'll just check 5 urls"
        how_many = 5

    #set up a Pool of processes based on how_many
    p = Pool(processes=how_many)
    # Gets a number of random starting urls based on how_many
    parse_us = [random_starting_url() for _ in range(how_many)]
    # Builds a list of urls mapped to each initial url
    data = p.map(get_links, [link for link in parse_us])
    # "Flattens out the list of urls"
    data = [url for url_list in data for url in url_list if "http" in url]
    # Close the processes
    p.close()

    # Write all of the found links into a text file for viewing
    with open("url.txt", "w") as f:
        f.write("\n".join(data))
    f.close()
    if raw_input("Print the urls to console? (type y for yes)\n").lower() == "y":
        for url in data:
            print url


if __name__ == '__main__':
    main(sys.argv)
