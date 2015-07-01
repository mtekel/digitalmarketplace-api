tsuru app-create digitalmarketplace-supplier-frontend python
tsuru service-add apisql postgresql shared
tsuru service-bind apisql
tsuru env-set \
DM_API_AUTH_TOKENS=ourtoken
DM_SEARCH_API_AUTH_TOKEN=CHbDLQtMvKoAuAtT8GM6vrdGGC
DM_SEARCH_API_URL=https://preview-search-api.development.digitalmarketplace.service.gov.uk
tsuru app-deploy *
