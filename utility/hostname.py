

def hostname_from_request(request):
    print(request.get_host())
    # split on `:` to remove port
    domain = request.get_host().split(":")[0].lower()
    try:
        domain_name = domain.split("www.", 1)[1]
        return domain_name
    except:
        return domain


def tenant_from_request(request):
    hostname = hostname_from_request(request)
    subdomain_prefix = hostname.split(".")[0]
    return subdomain_prefix


def tenant_outlet_type(request):
    return ""
