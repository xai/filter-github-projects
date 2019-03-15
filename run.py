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
    if 'last' in response.links:
        """This is a paginated list of results.
        We assume that 30 items are listed per page,
        so by knowing the last page number, we can calculate
        the total number without iterating through all pages.
        """
        url = response.links['last']['url']
        pattern = '.+\?page=(\d+).*'
        last_page = re.search(pattern, url).group(1)
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


def find_projects(min_issues, min_pulls, language, output_file=None):
    """TODO: read search criteria from cmd line args"""

    url = ('https://api.github.com/'
           'search/repositories?q=stars:100'
           '+pushed:>2017-01-01')

    if language:
        url = url + '+language:java'

    url = url + ('&sort=stars'
                 '&order=desc'
                 '&per_page=100'
                 '&page=1')

    response = query(url)
    result = json.loads(response.content.decode('utf-8'))

    csv_header = "User;Project;Stars;Language;Issues;Pull Requests;Url"
    if output_file:
        out = open(output_file, 'w')
        out.write(csv_header + '\n')
    else:
        print(csv_header)

    while True:
        """Loop over result pages until there is no 'next page' link."""

        for repo in result['items']:
            repo['lang'] = get_language(repo['languages_url'])
            repo['pulls'] = get_pulls(repo['pulls_url'])

            if min_issues > 0 and not repo['has_issues']:
                continue

            """Github treats pull requests as issues, so we have to subtract
            them from the number of issues in order to get the number of
            actual issues.
            """
            repo['issues'] = get_issues(repo['issues_url']) - repo['pulls']

            if repo['issues'] >= min_issues \
               and repo['pulls'] >= min_pulls \
               and repo['lang']:
                csv_row = '%s;%s;%d;%s;%s;%d;%s' % (repo['owner']['login'],
                                                    repo['name'],
                                                    repo['stargazers_count'],
                                                    repo['lang'],
                                                    repo['issues'],
                                                    repo['pulls'],
                                                    repo['html_url'])
                if output_file:
                    out.write(csv_row + '\n')
                else:
                    print(csv_row)
                    sys.stdout.flush()

        if 'next' in response.links:
            url = response.links['next']['url']
            response = query(url)
            result = json.loads(response.content.decode('utf-8'))
        else:
            break

    if output_file:
        out.close()

if __name__ == "__main__":
    global token
    global user

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output-file",
                        help="Output file",
                        default=None,
                        type=str)
    parser.add_argument("-i", "--min-issues",
                        help="Minimum number of issues",
                        default=0,
                        type=int)
    parser.add_argument("-p", "--min-pulls",
                        help="Minimum number of pull requests",
                        default=0,
                        type=int)
    parser.add_argument("-l", "--language",
                        help="Search for project using this language",
                        default=None,
                        type=str)
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

    find_projects(args.min_issues, args.min_pulls, args.language, args.output_file)
