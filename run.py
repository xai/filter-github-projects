#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Olaf Lessenich <xai@linux.com>
#
# Distributed under terms of the MIT license.

"""
Finds popular projects for research purposes on Github.

The goal is to filter the list of projects found
by criteria like minimum number or issues or pull requests.

TODO: - getting issue & pull request numbers
      - filtering of projects
      - search query without pre-selecting the language
"""

import argparse
import requests
import json


def get_language(url):
    response = requests.get(url, auth=(user, token))
    lang = ""
    size = 0

    if response.ok:
        result = json.loads(response.content.decode('utf-8'))
        for k,v in result.items():
            if v > size:
                size = v
                lang = k
        return lang
    else:
        response.raise_for_status()


def get_issues(url):
    # TODO
    return 0


def get_pulls(url):
    # TODO
    return 0


def find_projects():
    projects = []
    url = 'https://api.github.com/'
    query = 'search/repositories?q=stars:100+pushed:>2017-01-01&sort=stars&order=desc&per_page=100'

    #We need set at least one qualifier(q) and we can define if we want sort or order
    #We can find the syntax in:
    #(https://help.github.com/articles/searching-repositories/#search-based-on-when-a-repository-was-created-or-last-updated)
    #Example 1 - more than 1000 stars and pushed in 2017
    #search/repositories?q=stars:>1000+pushed:>2017
    #Example 2 - developed in java sort by stars, order desc and presenting 100 repositories per page
    #search/repositories?q=language:java&sort=stars&order=desc&per_page=100
 
    response = requests.get(url + query, auth=(user, token))
    if response.ok:
        result = json.loads(response.content.decode('utf-8'))
        for repo in result['items']:
            repo['lang'] = get_language(repo['languages_url'])
            repo['issues'] = get_issues(repo['issues_url'])
            repo['pulls'] = get_pulls(repo['pulls_url'])

            # TODO: filtering of projects
            projects.append(repo)
    else:
        response.raise_for_status()

    return projects


if __name__ == "__main__":
    global token
    global user

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token",
                        help="API token",
                        type=str,
                        required=True)
    parser.add_argument("-u", "--user",
                        help="Github user name",
                        type=str,
                        required=True)
    args = parser.parse_args()

    token = args.token
    user = args.user

    print('User;Project;Url;Stars;Language;Issues;Pull Requests')
    for p in find_projects():
        print('%s;%s;%s;%d,%s;%s;%d' % (p['owner']['login'],
                                        p['name'],
                                        p['html_url'],
                                        p['stargazers_count'],
                                        p['lang'],
                                        p['issues'],
                                        p['pulls']))
