# filter-github-projects
Find popular github projects (matching specified criteria) for research purposes.

## Setup
You have to register an API token first!  
Please see [this](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) on how to generate a token.

## Run
`./run.py -l <language> -u <username> -t <token>`

## TODO
- [ ] Retrieve number of issues + pull requests for each project
- [ ] Filter projects according to specified criteria
- [ ] Use pagination to retrieve more than 30 projects
- [ ] Find a way to specify the search query without specifying a language
