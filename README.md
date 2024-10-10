# Export a series of Confluence pages into PDF files

## Setup
1. Get yourself an [API token](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Copy `dotenv-example` into `.env` and edit the values with the correct ones, including your API token
3. Run `pipenv install` - if you don't have `pipenv`, install it first using your favourite way (e.g. `brew install pipenv`)

## Usage
Run it this way:
```
pipenv run export.py 'CQL search query' <output directory>
```

For example, to save all the pages with the label `label 1` but not the label `label 2` or `label 3`:
```
pipenv run export.py 'label="label 1" AND NOT (label = "label 2" OR label = "label 3")' ./pdf
```

This will download everything under the `./pdf` folder.
