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
        result = json.loads(response.content)
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
    query = 'search/repositories?q=language:%s&sort=stars&order=desc' % lang

    response = requests.get(url + query, auth=(user, token))

    if response.ok:
        result = json.loads(response.content)
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
