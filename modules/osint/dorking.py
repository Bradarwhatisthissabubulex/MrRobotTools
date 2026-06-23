"""[07] Dorking Query Engine - generate Google dorks for a target domain."""

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr

DORK_TEMPLATES = [
    ("Exposed files",        'site:{domain} ext:pdf | ext:doc | ext:docx | ext:xls | ext:xlsx | ext:txt'),
    ("Config / backup",      'site:{domain} ext:env | ext:bak | ext:old | ext:sql | ext:log | ext:conf'),
    ("Admin / login pages",  'site:{domain} inurl:admin OR inurl:login OR inurl:dashboard'),
    ("Directory listing",    'site:{domain} intitle:"index of"'),
    ("Error messages",       'site:{domain} "SQL syntax" OR "warning" OR "stack trace"'),
    ("Exposed passwords",    'site:{domain} intext:password | intext:credentials | intext:secret'),
    ("Subdomains (passive)", 'site:*.{domain} -site:www.{domain}'),
    ("WP exposure",          'site:{domain} inurl:wp-admin OR inurl:wp-content OR inurl:wp-config'),
    ("Open redirects",       'site:{domain} inurl:url= OR inurl:redirect= OR inurl:next='),
    ("File upload endpoints",'site:{domain} inurl:upload OR inurl:files OR inurl:attachment'),
    ("API docs",             'site:{domain} inurl:api OR inurl:swagger OR inurl:docs'),
    ("Git exposure",         'site:{domain} inurl:.git'),
    ("PHP info",             'site:{domain} inurl:phpinfo OR intitle:phpinfo'),
    ("Server status",        'site:{domain} inurl:server-status OR inurl:server-info'),
    ("Jenkins / CI",         'site:{domain} intitle:"Dashboard [Jenkins]" OR inurl:jenkins'),
]


def run():
    print(f"\n{BOLD}{DARK_GREEN}[07] DORKING QUERY ENGINE{RESET}")
    hr()
    print(f"{YELLOW}[!]{RESET} Generates Google search queries for a domain you own / are authorized to research.")
    domain = input(f"{GREEN}Target domain (e.g. example.com): {RESET}").strip()
    if not domain or "." not in domain:
        print(f"{RED}[-]{RESET} Invalid domain.")
        return
    domain = domain.replace("http://", "").replace("https://", "").rstrip("/")

    print(f"\n{CYAN}[i]{RESET} Generated dorks for {BOLD}{domain}{RESET}:\n")
    for i, (label, dork) in enumerate(DORK_TEMPLATES, 1):
        print(f"  {DARK_GREEN}[{i:02d}]{RESET} {CYAN}{label}{RESET}")
        print(f"       {GREEN}{dork.format(domain=domain)}{RESET}\n")

    save = input(f"{GREEN}Save all dorks to file? (path or Enter to skip): {RESET}").strip()
    if save:
        try:
            with open(save, "w", encoding="utf-8") as f:
                for label, dork in DORK_TEMPLATES:
                    f.write(f"# {label}\n{dork.format(domain=domain)}\n\n")
            print(f"{GREEN}[+]{RESET} Saved {len(DORK_TEMPLATES)} dorks to {save}")
        except Exception as e:
            print(f"{RED}[-]{RESET} Save failed: {e}")
