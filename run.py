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
"""

import argparse
import requests
import json
import re
import sys


def query(url):
    response = requests.get(url, auth=(user, token))

    if response.ok:
        return response
    else:
        response.raise_for_status()


def get_language(url):
    """Determines the language mostly used in a project."""

    lang = ""
    size = 0

    response = query(url)
    result = json.loads(response.content.decode('utf-8'))

    for k,v in result.items():
        if v > size:
            size = v
            lang = k

    return lang


def get_num_entries(url, key, arg=None):
    """Calculates the number of entries in a paginated list."""

    num_items = 0
    url = url.replace('{/number}', '?page=1')
    if arg:
        url = ''.join([url, '&', arg])

    response = query(url)
    last_link =  response.links.get('last', None)
    if last_link:
        """We have received a link header and parse the latest page."""
        pattern = '.+\?page=(\d+).*'
        last_page = re.search(pattern, last_link.get('url')).group(1)
        if last_page:
            url.replace('page=1', 'page=' + last_page)
            latest_items = query(url)
            num_items = 30 * (int(last_page) - 1) + \
                    len(json.loads(latest_items.content.decode('utf-8')))
    else:
        """There is no link header because the result is not paginated."""
        num_items = len(json.loads(response.content.decode('utf-8')))

    return num_items


def get_issues(url):
    return get_num_entries(url, 'issues', 'state=all')


def get_pulls(url):
    return get_num_entries(url, 'pulls', 'state=all')


def find_projects(min_issues, min_pulls):
    url = 'https://api.github.com/'
    search = ('search/repositories?q=stars:100'
             '+pushed:>2017-01-01'
             '&sort=stars'
             '&order=desc'
             '&per_page=100')

    """We need set at least one qualifier(q) and we can define if we want sort or order
    We can find the syntax in:
    (https://help.github.com/articles/searching-repositories/#search-based-on-when-a-repository-was-created-or-last-updated)
    Example 1 - more than 1000 stars and pushed in 2017
    search/repositories?q=stars:>1000+pushed:>2017
    Example 2 - developed in java sort by stars, order desc and presenting 100 repositories per page
    search/repositories?q=language:java&sort=stars&order=desc&per_page=100
    """
    page = 1
    pages = '&page='
    response = query(''.join([url, search, pages, str(page)]))
    totalResult = json.loads(response.content.decode('utf-8'))
    counter = totalResult.get('total_count')
    counter = counter - len(totalResult['items'])

    while counter > 0:
        page += 1
        response = query(''.join([url, search, pages, str(page)]))
        result = json.loads(response.content.decode('utf-8'))
        for repo in result['items']:
            totalResult['items'].append(repo)
        counter = counter - len(result['items'])
        repo['lang'] = get_language(repo['languages_url'])
        repo['pulls'] = get_pulls(repo['pulls_url'])

        if min_issues > 0 and not repo['has_issues']:
            continue

        """Github treats pull requests as issues, so we have to subtract
        them from the number of issues in order to get the number of
        actual issues.
        """
        repo['issues'] = get_issues(repo['issues_url']) - repo['pulls']

        if repo['issues'] >= min_issues and repo['pulls'] >= min_pulls and repo['lang']:
            file.write('%s;%s;%d;%s;%s;%d;%s\n' % (repo['owner']['login'],
                                            repo['name'],
                                            repo['stargazers_count'],
                                            repo['lang'],
                                            repo['issues'],
            sys.stdout.flush()
                                            repo['pulls'],
                                            repo['html_url']))


if __name__ == "__main__":
    global token
    global user

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--min-issues",
                        help="Minimum number of issues",
                        default=0,
                        type=int)
    parser.add_argument("-p", "--min-pulls",
                        help="Minimum number of pull requests",
                        default=0,
                        type=int)
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
    find_projects(args.min_issues, args.min_pulls)
