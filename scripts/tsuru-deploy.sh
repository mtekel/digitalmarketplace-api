tsuru app-create digitalmarketplace-api python
tsuru service-add postgresql marketplacedb shared
tsuru service-bind marketplacedb
tsuru env-set \
DM_API_AUTH_TOKENS=ourtoken
DM_SEARCH_API_AUTH_TOKEN=CHbDLQtMvKoAuAtT8GM6vrdGGC
DM_SEARCH_API_URL=https://preview-search-api.development.digitalmarketplace.service.gov.uk
tsuru app-deploy *

# Import suppliers
tsuru app-run 'python scripts/import_suppliers_from_api.py --users=password123 http://127.0.0.1:8888 ourtoken https://preview-api.development.digitalmarketplace.service.gov.uk wXeLg9vQNRqdkb9kccHDzFRaNL'

# Import services
tsuru app-run 'python scripts/import_services_from_api.py http://127.0.0.1:8888 ourtoken https://preview-api.development.digitalmarketplace.service.gov.uk wXeLg9vQNRqdkb9kccHDzFRaNL'

# Add cname (this is because SSL certificate is only for *.tsuru.paas.alphagov.co.uk)
# Add this to Route53 if you haven't done so already
tsuru cname-add digitalmarketplace-api-ci.tsuru.paas.alphagov.co.uk
