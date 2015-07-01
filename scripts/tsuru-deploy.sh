tsuru app-create digitalmarketplace-api python
tsuru service-add apisql postgresql shared
tsuru service-bind apisql
tsuru env-set \
DM_API_AUTH_TOKENS=ourtoken
DM_SEARCH_API_AUTH_TOKEN=CHbDLQtMvKoAuAtT8GM6vrdGGC
DM_SEARCH_API_URL=https://preview-search-api.development.digitalmarketplace.service.gov.uk
tsuru app-deploy *

# Import suppliers
tsuru app-run 'python scripts/import_suppliers_from_api.py --users=password http://127.0.0.1:8888 ourtoken https://preview-api.development.digitalmarketplace.service.gov.uk wXeLg9vQNRqdkb9kccHDzFRaNL'

# Import services
tsuru app-run 'python scripts/import_services_from_api.py http://127.0.0.1:8888 ourtoken https://preview-api.development.digitalmarketplace.service.gov.uk wXeLg9vQNRqdkb9kccHDzFRaNL'
